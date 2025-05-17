# tests/unit/server_models/test_function_tool_models.py

from llm_wrapper.server.models import FunctionCall, ToolCall, ToolChoice

def test_function_and_tool_model_construction():
    func_call = FunctionCall(name="fn", arguments="{}")
    assert func_call.name == "fn"

    tool_call = ToolCall(id="1", function=func_call)
    assert tool_call.id == "1"
    assert tool_call.function.name == "fn"

    tool_choice = ToolChoice(type="function", function={"name": "fn"})
    assert tool_choice.type == "function"
    assert tool_choice.function["name"] == "fn"