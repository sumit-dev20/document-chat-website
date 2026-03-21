from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_community.vectorstores import FAISS
from langchain_chroma import Chroma

load_dotenv(override=True)


llm = OllamaLLM(model="gpt-oss:20b")


def llm_response(query_text: str, collection_name: str) -> str:

    embedding_function = OpenAIEmbeddings()
    db = Chroma(
        collection_name=collection_name,
        embedding_function=embedding_function,
        persist_directory="chroma",
    )
    results = db.similarity_search_with_relevance_scores(query_text, k=5)
    if len(results) == 0 or results[0][1] < 0.7:
        return "Unable to find matching results."

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    print(context_text)

    PROMPT_TEMPLATE = """Answer the question based on the following context:
    
    {context}

    ---

    Answer the question based on the above context: {query}
    """

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, query=query_text)
    final_result = llm.invoke(prompt)

    print("final_result ==>> ", final_result)
    return final_result
