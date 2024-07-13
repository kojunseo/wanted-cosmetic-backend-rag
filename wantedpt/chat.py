import os

import requests
from typing import List, Dict

class WantBase:
    def __init__(self):
        project = os.getenv("WANTED_PROJECT")
        api_key = os.getenv("WANTED_API_KEY")
        self.header = {
            "project": project,
            "apiKey": api_key
        }

        self.api_url = "https://api-laas.wanted.co.kr/api/preset/chat/completions"
        self.messages = []
        self.params = {}
    
    def completions(self):
        body = {
            "params": self.params,
            "hash": self.hash,
            "messages": self.messages
        }
        response = requests.post(self.api_url, headers=self.header, json=body)
        return response.text


class WantedChat(WantBase):
    def __init__(self, hash: str):
        super().__init__()
        self.hash = hash

    def append(self, role: str, content: str):
        if role not in ["user", "assistant"]:
            raise ValueError("Invalid role. Please use 'user' or 'assistant'.")
        self.messages.append({"role": role, "content": content})

    def set_params(self, **kwargs):
        self.params = kwargs

    def __str__(self):
        output = f"""hash: {self.hash}
params: {self.params}
messages: {self.messages}"""
        return output
    
class WantedChatCompletions(WantBase):
    def __init__(self, hash: str):
        super().__init__()
        self.hash = hash

    def completions(self, messages: List[Dict[str, str]]=[], params: Dict[str, str]={}):
        body = {
            "params": params,
            "hash": self.hash,
            "messages": messages
        }
        response = requests.post(self.api_url, headers=self.header, json=body)
        response_dict = response.json()
        out= response_dict["choices"][0]["message"]["content"]
        return out
        

if __name__ == "__main__":
    chat = WantedChat("")
    chat.append("user", "안녕하세요")
    chat.set_params(task="가슴성형", context="유방 확대술")
    print(chat)
