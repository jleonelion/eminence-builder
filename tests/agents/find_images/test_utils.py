import pytest
from datetime import datetime
from agents.find_images.utils import *

# @pytest.fixture
# def state():
#     return GeneratePostState(
#         topic = "Test topic",
#         relevant_links=["https://www.google.com", "https://www.yahoo.com"],
#         report="Test report",
#     )

# @pytest.fixture
# def config():
#     return GeneratePostConfiguration()

def test_is_valid_url():
    assert is_valid_url("https://www.yahoo.com") == True
    assert is_valid_url("/test.jpg") == False
    assert is_valid_url("Just some text") == False

def test_extract_image_urls():
        text = "Here is an image ![alt text](https://example.com/image.jpg) and another one <img src=\"https://example.com/image2.png\">"
        urls = extract_image_urls(text)
        assert urls == ["https://example.com/image.jpg", "https://example.com/image2.png"]

        text = "No images here!"
        urls = extract_image_urls(text)
        assert urls == []

def test_filter_image_urls():
    urls = [
        "https://example.com/image.jpg",
        "https://example.com/image.svg",
        "https://example.com/image.png",
        "https://example.com/image.ico"
    ]
    filtered_urls = filter_image_urls(urls)
    assert filtered_urls == ["https://example.com/image.jpg", "https://example.com/image.png"]

def test_parse_validate_images_response():
    response = "<relevant_indices> 1, 2, 3 </relevant_indices>"
    assert parse_validate_images_response(response) == [1, 2, 3]

    response = "<relevant_indices> 4, 5, abc, 6 </relevant_indices>"
    assert parse_validate_images_response(response) == [4, 5, 6]

    response = "<relevant_indices> </relevant_indices>"
    assert parse_validate_images_response(response) == []

    response = "<relevant_indices> a, b, c </relevant_indices>"
    assert parse_validate_images_response(response) == []

    response = "No relevant indices here"
    assert parse_validate_images_response(response) == []