from mutations.Mutation import BaseMutation
from parse_dataset import parse_MBPP
import json

active_to_passive = BaseMutation(
    prompt="Change the following sentence to passive voice: {question}",
    dataset=parse_MBPP.load_MBPP_dataset(),
    output_path='mutation_output/active_passive_gpt-4o.jsonl',
    model='gpt-3.5-turbo'
)

declarative_to_interrogative = BaseMutation(
    prompt="Change the following sentence to interrogative voice: {question}",
    dataset=parse_MBPP.load_MBPP_dataset(),
    output_path='mutation_output/declarative_to_interrogative_gpt-3.5-turbo.jsonl',
    model='gpt-3.5-turbo'
)

verb_to_similar_verb = BaseMutation(
    prompt="Change the verbs of the following sentence to a similar verb: {question}",
    dataset=parse_MBPP.load_MBPP_dataset(),
    output_path='mutation_output/verb_to_similar_verb_gpt-3.5-turbo.jsonl',
    model='gpt-3.5-turbo'
)


if __name__ == '__main__':
    # active_to_passive.run()
    # declarative_to_interrogative.run()
    verb_to_similar_verb.run()