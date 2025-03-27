import json
import copy
import tqdm
import concurrent.futures as cfuts
from src import model

class BaseMutation:
    def __init__(self, prompt, dataset, output_path, model='gpt-3.5-turbo'):
        self.prompt = prompt
        self.dataset = dataset
        self.output_path = output_path
        self.model = model
    
    def form_messages(self):
        messages = []
        for per_data in self.dataset:
            question = per_data['question']
            message = [
                {'role': 'user', 'content': self.prompt.format(question=question)}
            ]
            messages.append(message)
        return messages
    
    def run_model(self, message):
        return model.call_chat_gpt(message, model=self.model)
    
    def run(self):
        messages = self.form_messages()

        def run_func(message, per_data):
            result = {}
            response, prompt_tokens, completion_tokens = self.run_model(message)
            result['task_id'] = per_data['task_id']
            result['original'] = per_data['question']
            result['mutation'] = response
            return result
        
        responses = []
        
        with cfuts.ThreadPoolExecutor(max_workers=32) as executor:
            futs = []
            for idx, per_data in enumerate(self.dataset):
                futs.append(executor.submit(run_func, messages[idx], per_data))

            for future in tqdm.tqdm(cfuts.as_completed(futs), total=len(futs)):
                responses.append(future.result())

        responses.sort(key=lambda x: int(x['task_id']))

        with open(self.output_path, 'a') as f:
            for res in responses:
                f.write(json.dumps(res) + "\n")

