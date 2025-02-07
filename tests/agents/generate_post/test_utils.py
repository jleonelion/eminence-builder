import pytest
from datetime import datetime
from agents.generate_post.state import GeneratePostState
from agents.generate_post.configuration import GeneratePostConfiguration
from agents.generate_post.utils import *
from langchain_core.messages import HumanMessage
from unittest.mock import MagicMock
from langgraph.store.base import BaseStore

@pytest.fixture
def state():
    return GeneratePostState(
        topic = "Test topic",
        relevant_links=["https://www.google.com", "https://www.yahoo.com"],
        report="Test report",
    )

@pytest.fixture
def config():
    return GeneratePostConfiguration()

@pytest.fixture
def mock_store():
    mock_store = MagicMock(spec=BaseStore)
    mock_store.aget.return_value = ""
    return mock_store


def test_remove_urls():
    cleaned = remove_urls("This is a test message with a url https://www.google.com")
    assert cleaned == "This is a test message with a url"

    cleaned = remove_urls("This is a test message with a url https://www.google.com and double  spaces")
    assert cleaned == "This is a test message with a url and double spaces"

def test_build_condense_post_system_prompt(state, config, mock_store):

    prompt = build_condense_post_system_prompt(state=state, config=config, original_post_length=len(state.post), store=mock_store)
    assert "Test report" in prompt
    assert "100" in prompt
    assert "https://www.google.com" in prompt
    assert "https://www.yahoo.com" in prompt
