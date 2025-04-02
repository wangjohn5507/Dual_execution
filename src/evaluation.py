import subprocess
import re
from typing import List, Dict, Any
import json

def execute_code(code, test_cases):
    full_test = '''{code}\n\n{test_case}'''
    results = []
    for test_case in test_cases:
        # print(full_test.format(code=code, test_case=test_case))
        process = subprocess.Popen(['python3', '-c', full_test.format(code=code, test_case=test_case)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = process.communicate(timeout=5)
            # Check if there was an assertion error in stderr
            if stderr or b'AssertionError' in stderr:
                # print(stderr)
                results.append(0)
            else:
                results.append(1)
        except Exception as e:
            process.kill()
            results.append(0)
    return results

def execute_code_file(code, test_cases):
    import tempfile
    import os
    import uuid
    
    results = []
    for test_case in test_cases:
        # Create temporary file with unique name using uuid
        unique_id = str(uuid.uuid4())
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f'test_{unique_id}.py')
        
        try:
            # Write to temp file
            with open(temp_file, 'w') as f:
                full_test = f"{code}\n\n{test_case}"
                f.write(full_test)

            # Run the temporary file
            process = subprocess.run(['python3', temp_file], 
                                  capture_output=True,
                                  timeout=5)
            
            # Check if there was an assertion error
            if process.stderr or b'AssertionError' in process.stderr:
                results.append(0)
            else:
                results.append(1)
                
        except Exception as e:
            results.append(0)
            
        finally:
            # Clean up temp file if it exists
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass
            
    return results



def is_assertion(text: str) -> bool:
    """
    Check if the given text is an assertion statement.
    
    Args:
        text (str): The text to check
        
    Returns:
        bool: True if the text is an assertion, False otherwise
    """
    # Remove whitespace and newlines
    text = text.strip()
    
    # Check for common assertion patterns
    assertion_patterns = [
        r'^assert\s+',  # Basic assert statement
        r'^self\.assert\w+\(',  # unittest style assertions
        r'^pytest\.assert\w+\(',  # pytest style assertions
        r'^self\.assert_',  # Another unittest style
        r'^assert_',  # Another common assertion style
        r'^assert\s+is\s+',  # assert is
        r'^assert\s+is\s+not\s+',  # assert is not
        r'^assert\s+in\s+',  # assert in
        r'^assert\s+not\s+in\s+',  # assert not in
        r'^assert\s+isinstance\(',  # assert isinstance
        r'^assert\s+issubclass\(',  # assert issubclass
        r'^assert\s+raises\(',  # assert raises
        r'^assert\s+equal\(',  # assert equal
        r'^assert\s+not\s+equal\(',  # assert not equal
        r'^assert\s+greater\(',  # assert greater
        r'^assert\s+less\(',  # assert less
        r'^assert\s+greater_equal\(',  # assert greater or equal
        r'^assert\s+less_equal\(',  # assert less or equal
    ]
    
    # Check if the text matches any assertion pattern
    for pattern in assertion_patterns:
        if re.match(pattern, text):
            return True
    
    return False


def ground_truth_test(path: str):
    data = list(map(json.loads, open(path)))
    test_cases = []
    for idx, data in enumerate(data):
        test_string = data['test']
        test_case = [test for test in test_string.split('\n') if test != '' and is_assertion(test)]
        test_cases.append(test_case)
    return test_cases

if __name__ == '__main__':
    code = 'print("Hello, World!")'
    test_cases = ['print("Hello, World!")', 'print("Hello, World!")']
    results = execute_code(code, test_cases)
    print(results)