from mutations.Mutation import BaseMutation
from parse_dataset import parse_MBPP
import json

active_passive = BaseMutation(
    prompt="Change the following sentence to passive voice: {question}",
    dataset=parse_MBPP.load_MBPP_dataset(),
    output_path='output/active_passive_gpt-4o.jsonl',
    model='gpt-4o'
)

active_passive.run()