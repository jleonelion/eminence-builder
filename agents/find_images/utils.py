import re
from typing import Optional, TypedDict
import validators
from agents.find_images.configuration import FindImagesConfiguration
from agents.find_images.state import FindImagesState
from agents.prompts import VALIDATE_IMAGES_PROMPT, RERANK_IMAGES_PROMPT
import mimetypes

def extract_image_urls(text: str) -> list[str]:
    """Extract image URLs from markdown and/or html content."""
    urls = []

    markdown_pattern = r'!\[.*?\]\((.*?)\)'
    urls.extend(re.findall(markdown_pattern, text))
    html_pattern = r'<img\s+[^>]*src="([^"]+)"'
    urls.extend(re.findall(html_pattern, text))

    return urls

BLACKLISTED_IMAGE_URL_ENDINGS = [".svg", ".ico", ".bmp"]

def filter_image_urls(urls: list[str]) -> list[str]:
    """Filter unwanted image URLs."""
    return [url for url in urls if not any(url.endswith(ending) for ending in BLACKLISTED_IMAGE_URL_ENDINGS)]

def is_valid_url(url: str) -> bool:
    """Check if a URL is valid."""
    try:
        return validators.url(url) == True
    except validators.ValidationFailure:
        return False

def build_validate_images_prompt(
    state: FindImagesState,
    config: FindImagesConfiguration,
) -> str:
    return VALIDATE_IMAGES_PROMPT.format(
        post=state.post,
        report=state.report,
    ) 

def chunk_array(array: list[str], size: int) -> list[list[str]]:
    """Chunk an array into smaller arrays."""
    return [array[i:i + size] for i in range(0, len(array), size)]

class ImageMessage(TypedDict):
    type: str
    text: Optional[str]
    file_uri: Optional[str]
    mime_type: Optional[str]
    image_url: Optional[dict[str, str]]
    
BLACKLISTED_MIME_TYPES = [
  "image/svg+xml",
  "image/x-icon",
  "image/bmp",
  "text/",
]

async def get_images_messages(chunk: list[str], base_index: int) -> list[ImageMessage]:
    """Get messages for images."""
    messages = []
    for index, url in enumerate(chunk):
        cleaned_url = remove_query_params(url)
        mime_type = get_mime_type(cleaned_url)
        # if the mime type is blacklisted, skip the image
        if not mime_type or any(mime_type.startswith(blacklisted) for blacklisted in BLACKLISTED_MIME_TYPES):
            continue
        else:
            # The structure of these messages will vary by model
            messages.append(
                ImageMessage(
                    type="text",
                    text=f"The below image is indexed at {index + base_index}",
                )
            )
            messages.append(
                ImageMessage(
                    type="image_url",
                    image_url={
                        "url": cleaned_url,
                    },
                    # TODO: or define these attirbutes if claud model is used
                    # type="media",
                    # file_uri=cleaned_url,
                    # mime_type=None,
                )
            )

    return messages

def remove_query_params(url: str) -> str:
    """Remove query parameters from a URL."""
    return url.split('?')[0]

def get_mime_type(url: str) -> Optional[str]:
    """Determine the MIME type of the provided URL string."""
    mime_type, _ = mimetypes.guess_type(url)
    return mime_type

def parse_validate_images_response (response: str) -> list[int]:
    """Parse the response from the image validation model."""

    relevant_indices_pattern = r'<relevant_indices>\s*([\d,\s\w]*?)\s*</relevant_indices>'
    match = re.findall(relevant_indices_pattern, response, re.DOTALL)
    if not match:
        return []
    indices_str = match[0]
    indices = indices_str.split(',')
    valid_indices = []
    for index in indices:
        index = index.strip()
        if index.isdigit():
            valid_indices.append(int(index))
    return valid_indices

def parse_rerank_images_response (response: str) -> list[int]:
    """Parse the response from the image ranking."""

    relevant_indices_pattern = r'<reranked-indices>\s*([\d,\s]*?)\s*</reranked-indices>'
    match = re.findall(relevant_indices_pattern, response, re.DOTALL)
    if not match:
        return []
    indices_str = match[0]
    indices = indices_str.split(',')
    valid_indices = []
    for index in indices:
        index = index.strip()
        if index.isdigit():
            valid_indices.append(int(index))
    return valid_indices

def build_rerank_images_prompt(
    state: FindImagesState,
    config: FindImagesConfiguration,
) -> str:
    return RERANK_IMAGES_PROMPT.format(
        post=state.post,
        report=state.report,
    ) 
