import pytest
from unittest.mock import AsyncMock, patch
from agents.verify_source.utils import get_url_contents, UrlContents
from agents.verify_source.state import VerifySingleLinkState
from agents.verify_source.configuration import VerifyLinksConfiguration

# @pytest.mark.asyncio
# async def test_get_url_contents():
#     state = VerifySourceInputState(url="http://example.com")
#     config = VerifySourceConfiguration()

#     mock_docs = [
#         AsyncMock(page_content="Content 1", metadata={"screenshot": "screenshot1.png", "image": ["image1.png"], "ogImage": ["ogImage1.png"]}),
#         AsyncMock(page_content="Content 2", metadata={"screenshot": "screenshot2.png", "image": ["image2.png"], "ogImage": ["ogImage2.png"]}),
#     ]

#     with patch("utils.FireCrawlLoader") as MockLoader:
#         mock_loader_instance = MockLoader.return_value
#         mock_loader_instance.aload.return_value = mock_docs

#         result = await get_url_contents(state, config)

#         assert result["content"] == "Content 1\nContent 2\n"
#         assert result["image_urls"] == ["image1.png", "ogImage1.png", "image2.png", "ogImage2.png"]

# @pytest.mark.asyncio
# async def test_get_url_contents_no_content():
#     state = VerifySourceInputState(url="http://example.com")
#     config = VerifySourceConfiguration()

#     mock_docs = []

#     with patch("utils.FireCrawlLoader") as MockLoader:
#         mock_loader_instance = MockLoader.return_value
#         mock_loader_instance.aload.return_value = mock_docs

#         with pytest.raises(ValueError, match=f"Failed to fetch content from {state.url}."):
#             await get_url_contents(state, config)

@pytest.mark.asyncio
async def test_get_firewcrawl():
    state = VerifySingleLinkState(link="https://firecrawl.dev")
    config = VerifyLinksConfiguration()

    result = await get_url_contents(state, config)
    # assert isinstance(result, UrlContents)
    assert len(result.content) > 0
    assert len(result.image_urls) == 1

