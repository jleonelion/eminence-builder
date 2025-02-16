"""Shared utility functions used in the project.

Functions:
    format_docs: Convert documents to an xml-formatted string.
    load_chat_model: Load a chat model from a model name.
"""

from dataclasses import field
import uuid
import json
from typing import Annotated, Any, Literal, Optional, Union
import validators
from pymongo import MongoClient
from agents.configuration import BaseConfiguration

from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langgraph.store.base import BaseStore
from enum import Enum
from urllib.parse import urlparse

RULESET_NAMESPACE = ["reflection_rules"]
RULESET_KEY = "ruleset"


async def fetch_rules(
    config: BaseConfiguration, post_style: str = "default"
) -> list[str]:
    """Retrieve persisted rules sets for a given post style.

    Args:
        store (BaseStore): The store to retrieve the ruleset from.
        post_style (str, optional): The style of post for these rules. Defaults to "default".

    Returns:
        list[str]: List of rules for post type.
    """

    collection = load_rules_collection(config)
    filter = {"post_style": post_style}
    rules_document = collection.find_one(filter)
    rules = rules_document["rules"] if rules_document else []
    return rules


async def store_rules(
    config: BaseConfiguration, rules: list[str], post_style: str = "default"
) -> None:
    """
    Stores rules for the given post type
    Args:
        config (BaseConfiguration): Configuration info used to connect to MongoDB.
        post_style (str, optional): The style of post for these rules. Defaults to "default".
    Returns:
        None
    """
    # only want one document of rules for each post_style, so we will update the existing document if it exists
    collection = load_rules_collection(config)
    filter = {"post_style": post_style}
    rules_document = collection.find_one(filter)

    if rules_document:
        collection.update_one(
            {"_id": rules_document["_id"]}, {"$set": {"rules": rules}}
        )
    else:
        collection.insert_one({"post_style": post_style, "rules": rules})


def _format_doc(doc: Document) -> str:
    """Format a single document as XML.

    Args:
        doc (Document): The document to format.

    Returns:
        str: The formatted document as an XML string.
    """
    metadata = doc.metadata or {}
    meta = "".join(f" {k}={v!r}" for k, v in metadata.items())
    if meta:
        meta = f" {meta}"

    return f"<document{meta}>\n{doc.page_content}\n</document>"


def format_docs(docs: Optional[list[Document]]) -> str:
    """Format a list of documents as XML.

    This function takes a list of Document objects and formats them into a single XML string.

    Args:
        docs (Optional[list[Document]]): A list of Document objects to format, or None.

    Returns:
        str: A string containing the formatted documents in XML format.

    Examples:
        >>> docs = [Document(page_content="Hello"), Document(page_content="World")]
        >>> print(format_docs(docs))
        <documents>
        <document>
        Hello
        </document>
        <document>
        World
        </document>
        </documents>

        >>> print(format_docs(None))
        <documents></documents>
    """
    if not docs:
        return "<documents></documents>"
    formatted = "\n".join(_format_doc(doc) for doc in docs)
    return f"""<documents>
{formatted}
</documents>"""


def load_chat_model(
    fully_specified_name: str, model_kwargs: Optional[dict[str, Any]] = None
) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
        model_kwargs (Optional[dict[str, Any]]): Additional keyword arguments for the model.
    """
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = ""
        model = fully_specified_name

    if model_kwargs is None:
        model_kwargs = {"temperature": 0}
    else:
        model_kwargs.setdefault("temperature", 0)

    if provider == "google_genai":
        model_kwargs["convert_system_message_to_human"] = True

    return init_chat_model(model, model_provider=provider, **model_kwargs)


def reduce_docs(
    existing: Optional[list[Document]],
    new: Union[
        list[Document],
        list[dict[str, Any]],
        list[str],
        str,
        Literal["delete"],
    ],
) -> list[Document]:
    """Reduce and process documents based on the input type.

    This function handles various input types and converts them into a sequence of Document objects.
    It also combines existing documents with the new one based on the document ID.

    Args:
        existing (Optional[Sequence[Document]]): The existing docs in the state, if any.
        new (Union[Sequence[Document], Sequence[dict[str, Any]], Sequence[str], str, Literal["delete"]]):
            The new input to process. Can be a sequence of Documents, dictionaries, strings, or a single string.
    """
    if new == "delete":
        return []

    existing_list = list(existing) if existing else []
    if isinstance(new, str):
        return existing_list + [
            Document(page_content=new, metadata={"uuid": str(uuid.uuid4())})
        ]

    new_list = []
    if isinstance(new, list):
        existing_ids = set(doc.metadata.get("uuid") for doc in existing_list)
        for item in new:
            if isinstance(item, str):
                item_id = str(uuid.uuid4())
                new_list.append(Document(page_content=item, metadata={"uuid": item_id}))
                existing_ids.add(item_id)

            elif isinstance(item, dict):
                metadata = item.get("metadata", {})
                item_id = metadata.get("uuid", str(uuid.uuid4()))

                if item_id not in existing_ids:
                    new_list.append(
                        Document(**item, metadata={**metadata, "uuid": item_id})
                    )
                    existing_ids.add(item_id)

            elif isinstance(item, Document):
                item_id = item.metadata.get("uuid")
                if item_id is None:
                    item_id = str(uuid.uuid4())
                    new_item = item.copy(deep=True)
                    new_item.metadata["uuid"] = item_id
                else:
                    new_item = item

                if item_id not in existing_ids:
                    new_list.append(new_item)
                    existing_ids.add(item_id)

    return existing_list + new_list


def unique_list(left: list[str], right: list[str]) -> list[str]:
    return list(dict.fromkeys(left + right))


UrlType = Annotated[
    Union[Literal["github", "youtube", "general", "twitter", "reddit"], None],
    field(default_factory=str),
]


# TODO: Implement support for different link types
def get_link_type(url: str) -> UrlType:
    """Determine the type of link."""
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname

    if "github" in hostname:
        return "github"
    if "youtube" in hostname:
        return "youtube"
    if "twitter" in hostname:
        return "twitter"
    if "reddit" in hostname:
        return "reddit"
    return "general"


def is_valid_url(url: str) -> bool:
    """Check if a URL is valid."""
    try:
        return validators.url(url) == True
    except validators.ValidationFailure:
        return False


def convert_md_to_unicode(text):
    # Unicode bold character mappings
    unicode_bold = {
        "a": "𝐚",
        "b": "𝐛",
        "c": "𝐜",
        "d": "𝐝",
        "e": "𝐞",
        "f": "𝐟",
        "g": "𝐠",
        "h": "𝐡",
        "i": "𝐢",
        "j": "𝐣",
        "k": "𝐤",
        "l": "𝐥",
        "m": "𝐦",
        "n": "𝐧",
        "o": "𝐨",
        "p": "𝐩",
        "q": "𝐪",
        "r": "𝐫",
        "s": "𝐬",
        "t": "𝐭",
        "u": "𝐮",
        "v": "𝐯",
        "w": "𝐰",
        "x": "𝐱",
        "y": "𝐲",
        "z": "𝐳",
        "A": "𝐀",
        "B": "𝐁",
        "C": "𝐂",
        "D": "𝐃",
        "E": "𝐄",
        "F": "𝐅",
        "G": "𝐆",
        "H": "𝐇",
        "I": "𝐈",
        "J": "𝐉",
        "K": "𝐊",
        "L": "𝐋",
        "M": "𝐌",
        "N": "𝐍",
        "O": "𝐎",
        "P": "𝐏",
        "Q": "𝐐",
        "R": "𝐑",
        "S": "𝐒",
        "T": "𝐓",
        "U": "𝐔",
        "V": "𝐕",
        "W": "𝐖",
        "X": "𝐗",
        "Y": "𝐘",
        "Z": "𝐙",
    }

    # Split text by bold markers
    parts = text.split("**")
    result = []

    # Convert alternating parts
    for i, part in enumerate(parts):
        if i % 2 == 1:  # Bold sections
            bold_text = "".join(unicode_bold.get(c, c) for c in part)
            result.append(bold_text)
        else:  # Regular text
            result.append(part)

    return "".join(result)


def load_linkedin_posts_collection(config: BaseConfiguration):
    db = init_db_connection(config=config)
    collection = db[config.mongo_collection_linkedin_posts]
    return collection


def load_rules_collection(config: BaseConfiguration):
    db = init_db_connection(config=config)
    collection = db[config.mongo_collection_rules]
    return collection


def init_db_connection(config: BaseConfiguration):
    client = MongoClient(config.mongo_url)
    db = client[config.mongo_db]
    return db
