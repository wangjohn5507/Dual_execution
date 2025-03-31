def process_generation_to_code(response):
    while '```python' in response:
        response = response.replace('```python', '')
    while '```' in response:
        response = response.replace('```', '')
    return response