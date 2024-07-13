from .chat import WantedChat, WantedChatCompletions

def run_completions(chain, params):
    return chain.completions(params=params)