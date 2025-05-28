import openai
from openai import OpenAI
import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import time


def call_chat_gpt(message, temperature=0.0, model="gpt-3.5-turbo"):
    wait = 1
    while True:
        try:
            ans = client.chat.completions.create(model=model,
            messages=message,
            temperature=temperature,
            n=1)
            return ans.choices[0].message.content, ans.usage.prompt_tokens, ans.usage.completion_tokens
        except openai.RateLimitError as e:
            time.sleep(min(wait, 60))
            wait *= 2