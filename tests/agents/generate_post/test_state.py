import pytest
from datetime import datetime
from agents.generate_post.state import GeneratePostState, PostDate, Image
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document

@pytest.fixture
def state():
    return GeneratePostState(
        topic="Test topic"
    )

def test_initialization():
    state = GeneratePostState(
        topic = "Test topic",
        links=["link1", "link2"],
        report="Test report",
        messages=[HumanMessage(content="Test message")],
        page_contents=[Document(page_content="content1"), Document(page_content="content2")],
        relevant_links=["link1", "link2"],
        post="Test post",
        schedule_date="p1",
        userResponse="Test response",
        next="schedulePost",
        image=Image(imageUrl="http://example.com/image.jpg", mimeType="image/jpeg"),
        condense_count=1
    )

    assert state.topic == "Test topic"
    assert state.links == ["link1", "link2"]
    assert state.report == "Test report"
    assert len(state.messages) == 1
    assert state.page_contents == [Document(page_content="content1"), Document(page_content="content2")]
    assert state.relevant_links == ["link1", "link2"]
    assert state.post == "Test post"
    assert state.schedule_date == "p1"
    assert state.userResponse == "Test response"
    assert state.next == "schedulePost"
    assert state.image["imageUrl"] == "http://example.com/image.jpg"
    assert state.image["mimeType"] == "image/jpeg"
    assert state.condense_count == 1

def test_default_initialization(state):
    assert state.topic == "Test topic"
    assert state.links == []
    assert state.report == ""
    assert state.messages == []
    assert state.page_contents == []
    assert state.relevant_links == []
    assert state.post == ""
    assert state.schedule_date is None
    assert state.userResponse is None
    assert state.next is None
    assert state.image is None
    assert state.condense_count == 0

def test_add_links(state):
    state.links = ["link1", "link2"]
    assert state.links == ["link1", "link2"]

def test_update_report(state):
    state.report = "Updated report"
    assert state.report == "Updated report"

def test_add_messages(state):
    message = HumanMessage(content="New message")
    state.messages.append(message)
    assert len(state.messages) == 1
    assert state.messages[0].content == "New message"

def test_update_post(state):
    state.post = "Updated post"
    assert state.post == "Updated post"

def test_update_schedule_date(state):
    state.scheduleDate = datetime.now()
    assert isinstance(state.scheduleDate, datetime)

def test_update_user_response(state):
    state.userResponse = "Updated response"
    assert state.userResponse == "Updated response"

def test_update_next(state):
    state.next = "rewritePost"
    assert state.next == "rewritePost"

def test_update_image(state):
    state.image = Image(imageUrl="http://example.com/new_image.jpg", mimeType="image/png")
    assert state.image["imageUrl"] == "http://example.com/new_image.jpg"
    assert state.image["mimeType"] == "image/png"

def test_increment_condense_count(state):
    state.condense_count += 1
    assert state.condense_count == 1