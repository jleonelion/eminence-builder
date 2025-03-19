import yaml  # noqa: D100
from langchain_core.documents import Document


def load_documents_from_yaml(yaml_file_path):
    """Load documents from a YAML file and convert them to LangChain Document objects.

    Args:
        yaml_file_path (str): Path to the YAML file

    Returns:
        list: A list of LangChain Document objects
    """
    with open(yaml_file_path) as file:
        yaml_data = yaml.safe_load(file)

    documents = []

    # Assuming the YAML has a 'reference_content' key with a list of documents
    for doc_data in yaml_data.get("reference_content", []):
        document = Document(
            page_content=doc_data.get("page_content", ""),
            metadata=doc_data.get("metadata", {}),
        )
        documents.append(document)

    return documents


# Example usage
yaml_file_path = (
    "/Users/jamesleone/code/eminence-builder/agents/write_blog_section/test.yaml"
)
documents = load_documents_from_yaml(yaml_file_path)

# Print the number of documents and the first document's content
print(f"Number of documents: {len(documents)}")  # noqa: T201
print("\nFirst document page content:")  # noqa: T201
print(documents[0].page_content[:500])  # Print first 500 characters  # noqa: T201
