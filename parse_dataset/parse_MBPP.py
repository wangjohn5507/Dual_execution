import json
import ast
import tqdm


file_path = 'dataset/MBPP_category.jsonl'
dataset = list(map(json.loads, open(file_path)))

def load_MBPP_dataset():
    final_dataset = []
    for idx, data in enumerate(tqdm.tqdm(dataset)):
        # prompt; task_id; ground_truth code; test; category; code_complexity
        record = dict()
        record['question'] = data['text']
        record['task_id'] = idx
        final_dataset.append(record)
    return final_dataset