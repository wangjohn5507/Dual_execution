import json
import copy
import tqdm
import concurrent.futures as cfuts
from src import model, utils


def form_messages(problems, is_test_case=False):
    return [
        [
            {'role': 'system', 'content': 'Generate the python code solution based on the context. Return the function with import packages if needed. Do not include any test cases or usage.' if not is_test_case else 'Complete the assertions with at least 5 test cases.'},
            {'role': 'user', 'content': problem}
        ]
        for problem in problems
    ]

def run_model(message):
    return model.call_chat_gpt(message, model='gpt-3.5-turbo')

def run(messages):
    def process_message(message, idx):
        response, prompt_tokens, completion_tokens = run_model(message)
        print(response)
        code = utils.process_generation_to_code(response)
        return {
            'task_id': idx,
            'prompt': message,
            'response': response,
            'response_code': code
        }

    with cfuts.ThreadPoolExecutor(max_workers=32) as executor:
        futures = [
            executor.submit(process_message, message, idx) 
            for idx, message in enumerate(messages)
        ]
        
        responses = []
        for future in tqdm.tqdm(cfuts.as_completed(futures), total=len(futures)):
            responses.append(future.result())

    responses.sort(key=lambda x: int(x['task_id']))

    with open(output_path, 'a') as f:
        for res in responses:
            f.write(json.dumps(res) + '\n')


if __name__ == '__main__':
    is_test_case = True
    type = 'code' if not is_test_case else 'test'
    dataset = 'mbpp'
    mutation_type = 'verb_to_similar_verb'
    model_name = 'gpt-3.5-turbo'
    mutation_file = f'mutation_output/{mutation_type}_{model_name}.jsonl'
    template_file = f'template_output/prompts_with_templates_{type}_{dataset}.jsonl'
    output_path = f'generation_output/{type}_{mutation_type}.jsonl'

    # Load data files
    with open(mutation_file) as f:
        mutations = [json.loads(line) for line in f]
    with open(template_file) as f:
        template_data = [json.loads(line) for line in f]

    # Filter mutations to match template data
    idxs = {int(data['task_id'].split('/')[-1])-1 for data in template_data}
    mutation_data = [data for idx, data in enumerate(mutations) if idx in idxs]

    # Generate problems from templates
    problems = [
        data['template'].format(
            function_name='func',
            problem=mutation_data[idx]['mutation']
        )
        for idx, data in enumerate(template_data)
    ]

    messages = form_messages(problems, is_test_case)
    run(messages[:100])








