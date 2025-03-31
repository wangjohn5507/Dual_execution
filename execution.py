from src.evaluation import execute_code, is_assertion
import json
import ast
import tqdm
from collections import Counter

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

if __name__ == '__main__':
    mutation_type_list = ['active_to_passive', 'declarative_to_interrogative', 'verb_to_similar_verb']
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
    for idx in tqdm.tqdm(solutions):
        execution_results[idx] = []
        for solution in solutions[idx]:
            # Standardize function name in solution
            standardized_solution = standardize_function_name(solution)
            # print(f"Standardized solution for index {idx}: {standardized_solution}")
            # Standardize function name in test cases
            standardized_tests = [standardize_function_name(test) for test in test_cases[idx]]
            # print(f"Standardized tests for index {idx}: {standardized_tests}")
            results = execute_code(standardized_solution, standardized_tests)
            execution_results[idx].append(results)
        # if idx == 10:
        #     break
    
    # print("\nFinal execution results:", execution_results)
    # Compute and print scores for each index
    for idx in execution_results:
        print(f"\nProcessing index {idx}:")
        scores = compute_score(execution_results[idx])
        print(f"Scores for index {idx}: {scores}")
        print(f"Execution results for index {idx}: {execution_results[idx]}")