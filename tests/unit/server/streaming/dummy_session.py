# tests/unit/server_streaming/dummy_session.py

class DummySession:
    def __init__(self, response): self._response = response
    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc, tb): pass
    def post(self, url, headers=None, json=None): return self._response