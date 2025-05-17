# tests/unit/server_api/dummy_responses.py

class DummyResponse200:
    def __init__(self, payload):
        self.status = 200
        self._payload = payload
        self.content = []

    async def text(self): return None
    async def json(self): return self._payload
    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc, tb): pass

class DummyResponseError:
    def __init__(self, status, text):
        self.status = status
        self._text = text
        self.content = []

    async def text(self): return self._text
    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc, tb): pass

class DummySession:
    def __init__(self, response): self._response = response
    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc, tb): pass
    def post(self, url, headers=None, json=None): return self._response