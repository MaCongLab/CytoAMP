import openai
import os
import requests
import re
from openai import OpenAI


token_key='your api key here'

# 设置缓存目录
cache_dir = "./model"
os.environ["TRANSFORMERS_CACHE"] = cache_dir

os.environ['OPENAI_API_KEY'] = token_key
client = OpenAI()


def GPT_QA(prompt, model_name="gpt-4o", api_key=None,input=None):
    if api_key is not None:
        openai.api_key = api_key
    else:
        openai.api_key = os.environ["OPENAI_API_KEY"]

    response = client.responses.create(
        model=model_name,
        instructions=prompt,
        input=input
    )
    return response.output_text

