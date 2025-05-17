# src/server/models.py

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, model_validator
import time
from llm_wrapper.lib.logging import setup_logger

logger = setup_logger("llm-server", "logs/server.log")

# ----------------------------
# Function and Tool Schemas
# ----------------------------

class FunctionCall(BaseModel):
    name: str
    arguments: str


class Function(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class ToolCall(BaseModel):
    id: str
    type: str = "function"
    function: FunctionCall


class ToolChoice(BaseModel):
    type: str = "function"
    function: Dict[str, str]


class Tool(BaseModel):
    type: str = "function"
    function: Function


# ----------------------------
# Message & Request Schemas
# ----------------------------

class Message(BaseModel):
    role: str
    content: Optional[str] = None
    name: Optional[str] = None
    function_call: Optional[FunctionCall] = None
    tool_calls: Optional[List[ToolCall]] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    functions: Optional[List[Function]] = None
    function_call: Optional[Union[str, Dict[str, str]]] = None
    tools: Optional[List[Tool]] = None
    tool_choice: Optional[Union[str, ToolChoice]] = None
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    top_k: Optional[int] = None  # ✅ FIXED: Added for compatibility with config
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None

    @model_validator(mode="before")
    def validate_functions_and_tools(cls, data):
        if isinstance(data, dict) and data.get("functions") and data.get("tools"):
            logger.warning("Both 'functions' and 'tools' provided in request. This is invalid.")
            raise ValueError("Cannot provide both 'functions' and 'tools'")
        return data


# ----------------------------
# Response Schemas
# ----------------------------

class ChatCompletionChoice(BaseModel):
    index: int
    message: Message
    finish_reason: Optional[str] = None


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Usage


class ChatCompletionChunkDelta(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None
    function_call: Optional[Dict[str, str]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class ChatCompletionChunkChoice(BaseModel):
    index: int
    delta: ChatCompletionChunkDelta
    finish_reason: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChatCompletionChunkChoice]


class ErrorResponse(BaseModel):
    error: Dict[str, Any]


# ----------------------------
# Model Registry Schema
# ----------------------------

class ModelData(BaseModel):
    id: str
    created: int = Field(default_factory=lambda: int(time.time()))


class ModelList(BaseModel):
    data: List[ModelData]