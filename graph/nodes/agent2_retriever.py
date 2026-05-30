"""
Agent 2 - RAG Retrieval Agent
------------------------------
Takes Agent 1 summary.
Searches IBM knowledge base for relevant documents.
Like a research assistant finding the right chapters.
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions

load_dotenv()
client = OpenAI()


def build_knowledge_base():
    """Build ChromaDB with IBM documents if not exists."""
    from finetune.data.ibm_docs import IBM_DOCS

    chroma_client = chromadb.PersistentClient(path="./chroma_db")

    ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="text-embedding-3-small"
    )

    try:
        collection = chroma_client.get_collection(
            "ibm_migration_docs",
            embedding_function=ef
        )
        print(f"  [Agent 2] Loaded existing KB: {collection.count()} docs")
    except Exception:
        collection = chroma_client.create_collection(
            "ibm_migration_docs",
            embedding_function=ef
        )
        collection.add(
            documents=[doc["text"] for doc in IBM_DOCS],
            ids=[doc["id"] for doc in IBM_DOCS],
            metadatas=[{"category": doc["category"]} for doc in IBM_DOCS]
        )
        print(f"  [Agent 2] Built KB: {len(IBM_DOCS)} IBM docs indexed")

    return collection


def agent2_retrieve(state: dict) -> dict:
    print("  [Agent 2] Retrieving IBM knowledge...")

    summary = state.get("infra_summary", {})
    collection = build_knowledge_base()

    # Generate targeted search queries based on infrastructure
    queries = [
        f"IBM Cloud migration {summary.get('migration_pattern', 'replatform')}",
        f"IBM Cloud compute servers {summary.get('total_servers', 0)} migration",
        f"IBM Cloud database migration {summary.get('total_databases', 0)}",
        "IBM Cloud compliance GDPR security",
        "IBM Cloud cost savings migration ROI",
    ]

    # Add complexity-specific query
    if summary.get("complexity_score", 0) > 7:
        queries.append("IBM Cloud complex migration legacy systems blockers")

    all_chunks = []
    seen_ids = set()

    for query in queries:
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        for i, doc in enumerate(results["documents"][0]):
            doc_id = results["ids"][0][i]
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                all_chunks.append({
                    "id": doc_id,
                    "text": doc,
                    "category": results["metadatas"][0][i].get("category")
                })

    print(f"  [Agent 2] Retrieved {len(all_chunks)} unique IBM knowledge chunks")

    return {
        **state,
        "rag_chunks": all_chunks,
        "retrieval_queries": queries,
        "current_node": "agent2"
    }
