import os
from typing import List, Dict
from opentelemetry import trace

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader

tracer = trace.get_tracer("rag")

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "vectorDB")
DATA_DIR   = os.path.join(os.path.dirname(__file__), "..", "data")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_vectorstore = None


def _get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
    )


def build_vectorstore() -> None:
    """Load documents from data/ and index them into ChromaDB."""
    with tracer.start_as_current_span("build_vectorstore"):
        print("[RAG] Building vector store from data/ ...")
        loader = DirectoryLoader(DATA_DIR, glob="**/*.txt", loader_cls=TextLoader)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)

        embeddings = _get_embeddings()
        db = Chroma.from_documents(
            chunks,
            embeddings,
            persist_directory=CHROMA_DIR,
        )
        db.persist()
        print(f"[RAG] Indexed {len(chunks)} chunks into ChromaDB.")


def _load_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        if not os.path.exists(CHROMA_DIR) or not os.listdir(CHROMA_DIR):
            build_vectorstore()
        _vectorstore = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=_get_embeddings(),
        )
    return _vectorstore


def retrieve(query: str, emotion_context: str = "", k: int = 3) -> List[Dict]:
    """
    Retrieve top-k relevant documents for the query + emotion context.
    Returns list of {"content": ..., "source": ..., "score": ...}
    """
    with tracer.start_as_current_span("retrieve") as span:
        augmented_query = f"{emotion_context}. {query}" if emotion_context else query
        span.set_attribute("query", augmented_query)
        span.set_attribute("k", k)

        db = _load_vectorstore()
        results = db.similarity_search_with_relevance_scores(augmented_query, k=k)

        docs = []
        for i, (doc, score) in enumerate(results):
            span.set_attribute(f"doc_{i}_score", round(score, 4))
            span.set_attribute(f"doc_{i}_source", doc.metadata.get("source", "unknown"))
            docs.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "score": round(score, 4),
            })

        return docs
