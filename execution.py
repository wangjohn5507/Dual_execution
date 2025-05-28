from src.evaluation import execute_code, is_assertion, ground_truth_test, execute_code_file, ground_truth_solution
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

def compute_test_score(test_results):
    if not test_results:
        return []
        
    print("\nComputing scores for test cases:", test_results)
    
    # Count frequency of each test result
    result_counts = Counter(tuple(result) for result in test_results)
    print("Test result counts:", result_counts)
    
    # Calculate score for each test case
    scores = []
    for result in test_results:
        passing_solutions = sum(1 for x in result if x == 1)
        # Get frequency of this test result
        frequency = result_counts[tuple(result)]
        # Calculate score: frequency * test result (1 for pass, 0 for fail)
        score = frequency * passing_solutions
        print(f"Test result {result}: frequency={frequency}, passing_solutions={passing_solutions}, score={score}")
        scores.append(score)
    
    return scores

def select_best_solutions(solutions, scores):
    if not scores:
        return []
    
    max_score = max(scores)
    best_indices = [i for i, score in enumerate(scores) if score == max_score]
    best_solutions = [solutions[i] for i in best_indices]
    return best_solutions

def select_best_tests(test_cases, scores):
    if not scores:
        return []
    
    max_score = max(scores)
    best_indices = [i for i, score in enumerate(scores) if score == max_score]
    best_tests = [test_cases[i] for i in best_indices]
    return best_tests

def seperate_assertions(test_string):
    test_list = []
    tests = [test.strip() for test in test_string.split('\n') if test.strip() != '']
    record = ''
    for test in tests:
        if test.startswith('assert'):
            if record:
                test_list.append(record + '\n' + test)
                record = ''
            else:
                test_list.append(test)
        else:
            record += '\n' + test
    if record:
        test_list.append('assert ' + record)
    return test_list

def evaluate_solutions(execution_results, golden_test_cases, solutions):
    # Track total solutions and correct solutions
    chosen_solutions = dict()
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
            chosen_solution = random.choice(best_solutions)
            chosen_solutions[idx] = chosen_solution
            print(f"Selected chosen solution for index {idx}")
            
            # Test golden solution with ground-truth test cases
            standardized_solution = standardize_function_name(chosen_solution)
            standardized_tests = [standardize_assertion_name(test) for test in golden_test_cases[idx]]
            print(f"Standardized tests: {standardized_tests}")
            results = execute_code_file(standardized_solution, standardized_tests)
            print(f"Golden solution test results: {results}")
            print(f"Chosen solution: {standardized_solution}")
            
            # Count total and correct solutions
            total_solutions += 1
            if all(result == 1 for result in results):
                correct_solutions += 1
                print(f"Solution {idx} passed all golden test cases!")
            else:
                print(f"Solution {idx} failed some golden test cases.")
    
    # Calculate and print accuracy for solutions
    solution_accuracy = (correct_solutions / total_solutions) * 100 if total_solutions > 0 else 0
    print(f"\nSolution Accuracy: {solution_accuracy:.2f}% ({correct_solutions}/{total_solutions} solutions passed all golden test cases)")


def evaluate_tests(test_results, golden_solutions, test_cases):
    total_solutions = 0
    correct_solutions = 0
    chosen_test_dict = {}
    
    for idx in test_results:
        scores = compute_test_score(test_results[idx])
        print(f"Scores for index {idx}: {scores}")
        best_tests = select_best_tests(test_cases[idx], scores)
        print(f"Best test for index {idx}: {best_tests}")

        if best_tests:
            num = min(len(best_tests), 5)
            chosen_test = random.sample(best_tests, num)
            chosen_test_dict[idx] = chosen_test

            standardized_solution = standardize_function_name(golden_solutions[idx])
            standardized_tests = [standardize_assertion_name(test) for test in chosen_test]
            print(f"Standardized tests: {standardized_tests}")
            results = execute_code_file(standardized_solution, standardized_tests)
            print(f"Results: {results}")
            print(f"Golden solution: {standardized_solution}")
            print(f"Chosen test solution: {standardized_tests}")

            total_solutions += 1
            if all(result == 1 for result in results):
                correct_solutions += 1
                print(f"Solution {idx} passed all golden test cases!")
            else:
                print(f"Solution {idx} failed some golden test cases.")
    
    # Calculate and print accuracy for solutions
    solution_accuracy = (correct_solutions / total_solutions) * 100 if total_solutions > 0 else 0
    print(f"\nSolution Accuracy: {solution_accuracy:.2f}% ({correct_solutions}/{total_solutions} solutions passed all golden test cases)")


        
            
            
    

if __name__ == '__main__':
    random.seed(42)
    mutation_type_list = ['original', 'active_to_passive', 'declarative_to_interrogative', 'verb_to_similar_verb', 'lowercase_to_uppercase', 'add_precision', 'rephrase_sentence']
    mutation_type_list = ['original', 'lowercase_to_uppercase']
    model_name = 'o3-mini'

    solutions = dict()
    test_cases = dict()
    execution_results = dict()  # Dictionary to store execution results
    
    for mutation_type in mutation_type_list:
        generated_data = list(map(json.loads, open(f'generation_output/code_{mutation_type}_{model_name}.jsonl')))
        for idx, data in enumerate(generated_data):
            solutions[idx] = solutions.get(idx, []) + [data['response_code']]
    
    for mutation_type in mutation_type_list:
        generated_test = list(map(json.loads, open(f'generation_output/test_{mutation_type}_{model_name}.jsonl')))
        for idx, test in enumerate(generated_test):
            tests = seperate_assertions(test['response_code'])
            test_cases[idx] = test_cases.get(idx, []) + tests
    
    # Execute each solution with its corresponding test cases
    def process_solution(args):
        idx, solution, test_cases_idx = args
        # Standardize function name in solution
        standardized_solution = standardize_function_name(solution)
        # Standardize function name in test cases 
        standardized_tests = [standardize_assertion_name(test) for test in test_cases_idx]
        results = execute_code_file(standardized_solution, standardized_tests)
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
    
    # # Select best solutions and choose golden solution
    
    dataset = 'mbpp'
    golden_test_cases = ground_truth_test(f'dataset/{dataset}_sanitized_for_code_generation.jsonl')
    golden_test_cases = golden_test_cases[:20]

    evaluate_solutions(execution_results, golden_test_cases, solutions)

    # golden_solutions = ground_truth_solution(f'dataset/{dataset}_sanitized_for_code_generation.jsonl')
    # test_results = dict()
    # def process_test(args):
    #     idx, solutions, test_case = args
    #     results = []
    #     # Standardize function name in solution
    #     standardized_solutions = [standardize_function_name(solution) for solution in solutions]
    #     # Standardize function name in test cases 
    #     standardized_tests = [standardize_assertion_name(test_case)]
    #     for standardized_solution in standardized_solutions:
    #         results.append(execute_code_file(standardized_solution, standardized_tests)[0])
    #     return idx, solutions, results

    # with cfuts.ThreadPoolExecutor(max_workers=32) as executor:
    #     tasks = []
    #     for idx in test_cases:
    #         # Initialize execution_results with empty lists for each test case
    #         test_results[idx] = []
    #         for test_case in test_cases[idx]:
    #             tasks.append((idx, solutions[idx], test_case))
        
    #     for idx, solutions, results in tqdm.tqdm(executor.map(process_test, tasks), total=len(tasks)):
    #         # For each test case, append the execution result to its list
    #         # print(idx, results)
    #         test_results[idx].append(results)

    # evaluate_tests(test_results, golden_solutions, test_cases)

    

    
    
    
    
  