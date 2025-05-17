# tests/unit/client_cli/dummy_openai.py

class DummyMessage:
    def __init__(self, content):
        self.content = content

class DummyResponse:
    def __init__(self, content, stream=False):
        self._content = content
        self.stream = stream
        self.choices = [type("X", (), {"message": DummyMessage(content)})()]

    def __iter__(self):
        if self.stream:
            for word in self._content.split():
                yield type("Chunk", (), {
                    "choices": [
                        type("Delta", (), {"delta": type("DeltaContent", (), {"content": word + " "})()})
                    ]
                })()
        else:
            raise TypeError("DummyResponse is not iterable unless stream=True")

class DummyOpenAI:
    def __init__(self, base_url, api_key): pass

    @property
    def chat(self): return self
    @property
    def completions(self): return self

    def create(self, model, messages, temperature=None, stream=False):
        return DummyResponse("hello world", stream=stream)