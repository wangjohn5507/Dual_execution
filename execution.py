from src.evaluation import execute_code, is_assertion, ground_truth_test
import json
import ast
import tqdm
import random
from collections import Counter
import concurrent.futures as cfuts
import re

def standardize_function_name(code):
    try:
        # Parse the code into an AST
        tree = ast.parse(code)
        
        # Find the last function definition
        original_name = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                original_name = node.name
        
        if original_name:
            # Replace all occurrences of the original function name with 'func'
            code = code.replace(original_name, 'func')
            
    except SyntaxError:
        # If the code can't be parsed, return it as is
        pass
    
    return code

def standardize_assertion_name(test_case):
    # Remove leading/trailing whitespace
    test_case = test_case.strip()
    # print(f"Original test case: {test_case}")
    
    # List of built-in functions to skip
    builtin_funcs = ['set', 'len', 'sum', 'max', 'min', 'sorted', 'list', 'tuple', 'dict', 'str', 'int', 'float', 'bool']
    
    # Find the first function name after 'assert' that's not a built-in
    parts = test_case.split('assert ')
    if len(parts) > 1:
        rest = parts[1]
        # Handle built-in functions
        for builtin in builtin_funcs:
            if rest.startswith(f'{builtin}('):
                # Skip past the built-in function
                rest = rest[len(builtin)+1:]  # Skip past 'builtin('
                # Find the next function name
                func_parts = rest.split('(', 1)
                if len(func_parts) > 1:
                    # Replace function name with 'func'
                    standardized_test = f'assert {builtin}(func(' + func_parts[1]
                    # print(f"Standardized test: {standardized_test}")
                    return standardized_test
        
        # Handle normal case without built-in functions
        func_parts = rest.split('(', 1)
        if len(func_parts) > 1:
            # Replace function name with 'func'
            standardized_test = 'assert func(' + func_parts[1]
        else:
            standardized_test = test_case
    else:
        standardized_test = test_case
    
    # print(f"Standardized test: {standardized_test}")
    return standardized_test

def compute_score(execution_results):
    if not execution_results:
        return []
        
    print("\nComputing scores for execution results:", execution_results)
    
    # Count frequency of each result
    result_counts = Counter(tuple(result) for result in execution_results)
    print("Result counts:", result_counts)
    
    # Calculate score for each result
    scores = []
    for result in execution_results:
        # Count number of passing tests (1s) in the result
        passing_tests = sum(1 for x in result if x == 1)
        # Get frequency of this result
        frequency = result_counts[tuple(result)]
        # Calculate score: frequency * number of passing tests
        score = frequency * passing_tests
        print(f"Result {result}: frequency={frequency}, passing_tests={passing_tests}, score={score}")
        scores.append(score)
    
    return scores

def select_best_solutions(solutions, scores):
    if not scores:
        return []
    
    max_score = max(scores)
    best_indices = [i for i, score in enumerate(scores) if score == max_score]
    best_solutions = [solutions[i] for i in best_indices]
    return best_solutions

if __name__ == '__main__':
    random.seed(42)
    mutation_type_list = ['original', 'active_to_passive', 'declarative_to_interrogative', 'verb_to_similar_verb', 'lowercase_to_uppercase', 'add_precision', 'rephrase_sentence']
    solutions = dict()
    test_cases = dict()
    execution_results = dict()  # Dictionary to store execution results
    
    for mutation_type in mutation_type_list:
        generated_data = list(map(json.loads, open(f'generation_output/code_{mutation_type}.jsonl')))
        for idx, data in enumerate(generated_data):
            solutions[idx] = solutions.get(idx, []) + [data['response_code']]
    
    for mutation_type in mutation_type_list:
        generated_test = list(map(json.loads, open(f'generation_output/test_{mutation_type}.jsonl')))
        for idx, test in enumerate(generated_test):
            tests = [test for test in test['response_code'].split('\n') if test != '' and is_assertion(test)]
            test_cases[idx] = test_cases.get(idx, []) + tests
    
    # Execute each solution with its corresponding test cases
    def process_solution(args):
        idx, solution, test_cases_idx = args
        # Standardize function name in solution
        standardized_solution = standardize_function_name(solution)
        # Standardize function name in test cases 
        standardized_tests = [standardize_assertion_name(test) for test in test_cases_idx]
        results = execute_code(standardized_solution, standardized_tests)
        return idx, results

    with cfuts.ThreadPoolExecutor(max_workers=32) as executor:
        tasks = []
        for idx in solutions:
            execution_results[idx] = []
            for solution in solutions[idx]:
                tasks.append((idx, solution, test_cases[idx]))
        
        for idx, results in tqdm.tqdm(executor.map(process_solution, tasks), total=len(tasks)):
            execution_results[idx].append(results)
        # if idx == 100:
        #     break
    
    # Select best solutions and choose golden solution
    golden_solutions = {}
    dataset = 'mbpp'
    golden_test_cases = ground_truth_test(f'dataset/{dataset}_sanitized_for_code_generation.jsonl')
    
    # Track total solutions and correct solutions
    total_solutions = 0
    correct_solutions = 0
    
    for idx in execution_results:
        print(f"\nProcessing index {idx}:")
        scores = compute_score(execution_results[idx])
        print(f"Scores for index {idx}: {scores}")
        
        # Select best solutions
        best_solutions = select_best_solutions(solutions[idx], scores)
        print(f"Best solutions for index {idx}: {len(best_solutions)} solutions with score {max(scores)}")
        
        # Randomly select one as golden solution
        if best_solutions:
            golden_solution = random.choice(best_solutions)
            golden_solutions[idx] = golden_solution
            print(f"Selected golden solution for index {idx}")
            
            # Test golden solution with ground-truth test cases
            standardized_solution = standardize_function_name(golden_solution)
            standardized_tests = [standardize_assertion_name(test) for test in golden_test_cases[idx]]
            print(f"Standardized tests: {standardized_tests}")
            results = execute_code(standardized_solution, standardized_tests)
            print(f"Golden solution test results: {results}")
            print(f"Golden solution: {golden_solution}")
            
            # Count total and correct solutions
            total_solutions += 1
            if all(result == 1 for result in results):
                correct_solutions += 1
                print(f"Solution {idx} passed all golden test cases!")
            else:
                print(f"Solution {idx} failed some golden test cases.")
    
    # Calculate and print accuracy
    accuracy = (correct_solutions / total_solutions) * 100 if total_solutions > 0 else 0
    print(f"\nAccuracy: {accuracy:.2f}% ({correct_solutions}/{total_solutions} solutions passed all golden test cases)")