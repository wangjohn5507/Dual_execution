#!/usr/bin/env python3

import json
import re
import os

def process_prompt(prompt: str) -> str:
    # Extract the original function name
    function_match = re.search(r'def\s+(\w+)\s*\(', prompt)
    original_function = function_match.group(1) if function_match else "FUNCTION_NAME"
    
    # Extract the original problem description
    problem_match = re.search(r'[\'"]{3}(.*?)[\'"]{3}', prompt, flags=re.DOTALL)
    original_problem = problem_match.group(1).strip() if problem_match else "PROBLEM_DESCRIPTION"
    
    # Create template with placeholders
    template = prompt
    template = re.sub(r'def\s+(\w+)\s*\(', 'def {function_name}(', template)
    template = re.sub(r'[\'"]{3}(.*?)[\'"]{3}', lambda m: '\'\'\'\n    {problem}\n    \'\'\'', template, flags=re.DOTALL)
    
    # Replace any remaining function names in the code body
    template = re.sub(r'\b(?!def\s+)(\w+)\s*\(', '{function_name}(', template)
    template = template.replace(original_function, "{function_name}")
    
    return template, original_function, original_problem

def extract_prompts():
    # Path to the input and output JSONL files
    input_file = "dataset/mbpp_sanitized_for_code_generation.jsonl"
    output_file = "template_output/prompts_with_templates_code.jsonl"
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line in infile:
                try:
                    data = json.loads(line.strip())
                    prompt = data.get('prompt', '')
                    task_id = data.get('task_id', '')
                    if prompt:
                        # Process the prompt to create template
                        template, original_function, original_problem = process_prompt(prompt)
                        
                        # Verify template can be formatted
                        try:
                            formatted = template.format(
                                function_name=original_function,
                                problem=original_problem
                            )
                            assert formatted == prompt, "Template formatting failed to reproduce original prompt"
                        except Exception as e:
                            print(f"Template formatting failed: {str(e)}")
                            print(f"Prompt: {prompt}")
                            print(f"Formatted: {formatted}")
                            print(f"Template: {template}")
                            print(f"Original function: {original_function}")
                            print(f"Original problem: {original_problem}")
                    # Create output record
                        output_record = {
                            'task_id': task_id,
                            'original_prompt': prompt,
                            'template': template,
                            'original_function': original_function,
                            'original_problem': original_problem
                        }
                        
                        # Write to output file
                        outfile.write(json.dumps(output_record) + '\n')
                        
                        # Print progress
                        # print(f"Processed prompt with function: {original_function}")
                        
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON line: {str(e)}")
                    continue
                except Exception as e:
                    print(f"Error processing prompt: {str(e)}")
                    continue
                    
        print(f"\nProcessing complete. Results saved to {output_file}")
        
    except Exception as e:
        print(f"Error reading/writing files: {str(e)}")

if __name__ == "__main__":
    extract_prompts() 