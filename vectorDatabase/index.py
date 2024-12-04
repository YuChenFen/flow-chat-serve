import chromadb
from chromadb.utils import embedding_functions

ef = embedding_functions.SentenceTransformerEmbeddingFunction("./models/all-MiniLM-L6-v2")
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="my_collection", embedding_function=ef)
MAX_BATCH_SIZE = 3000


def vd_query(documents: list, query: str, n_results: int = 5):
    documents_len = len(documents)
    for i in range(0, documents_len, MAX_BATCH_SIZE):
        collection.upsert(
            documents=documents[i:i+MAX_BATCH_SIZE],
            ids=[ f"id{index}" for index in range(i, min(i+MAX_BATCH_SIZE, documents_len)) ]
        )
    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, documents_len),
        include=["documents"]
    )

    # collection.delete(ids=[ f"id{i}" for i in range(len(documents)) ])
    for i in range(0, documents_len, MAX_BATCH_SIZE):
        collection.delete(ids=[ f"id{index}" for index in range(i, min(i+MAX_BATCH_SIZE, documents_len)) ])
    return results['documents'][0]

if __name__ == "__main__":
    print(vd_query(["hello world", "bad end"], "hello"))
