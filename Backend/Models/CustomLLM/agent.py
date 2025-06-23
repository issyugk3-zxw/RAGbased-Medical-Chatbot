import os
from openai import OpenAI


class Agent:
    def __init__(self):
        self.api_key = "put your api key here"
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

