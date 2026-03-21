from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
import os
import tempfile
from dotenv import load_dotenv
import uuid

load_dotenv(override=True)


def load_documents(uploaded_file):

    suffix = os.path.splitext(uploaded_file.name)[1]  # e.g. ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    if suffix == ".pdf":
        loader = PyPDFLoader(tmp_path)
    elif suffix == ".txt":
        loader = TextLoader(tmp_path)
    elif suffix == ".md":
        loader = UnstructuredMarkdownLoader(tmp_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    # documents = loader.load()

    # loader = DirectoryLoader(DATA_PATH, glob="*.md")
    # loader = PyPDFDirectoryLoader(DATA_PATH, glob="*.pdf")
    documents = loader.load()
    return documents


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    document = chunks[0]
    print(document.page_content)
    print(document.metadata)

    return chunks


def save_to_database(chunks: list[Document]) -> str:

    embedding_function = OpenAIEmbeddings()

    collection_name = str(uuid.uuid4())

    db = Chroma.from_documents(
        documents=chunks,
        collection_name=collection_name,
        embedding=embedding_function,
        persist_directory="chroma",
    )

    print(f"Saved {len(chunks)} chunks using Chroma")
    return collection_name


def create_databse(uploaded_file) -> str:
    documents = load_documents(uploaded_file)
    chunks = split_text(documents)
    name = save_to_database(chunks)
    return name
