from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma

embedding = SentenceTransformerEmbeddings(model_name="./models/all-MiniLM-L6-v2")

def retriever_query(documents, query_list, n=250, w=0.5):
    n_results = n // len(query_list)
    bm25_retriever = BM25Retriever.from_texts(documents)
    bm25_retriever.k = n_results

    chroma_db = Chroma.from_texts(documents, embedding=embedding)
    chroma_retriever = chroma_db.as_retriever(search_kwargs={"k": n_results})

    ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, chroma_retriever], weights=[w, 1-w])
    result = set()
    for query in query_list:
        result_q = ensemble_retriever.get_relevant_documents(query)
        for doc in [doc.page_content for doc in result_q][:n_results]:
            if doc not in result: result.add(doc)
    chroma_db.delete_collection()
    return list(result)

if __name__ == "__main__":
    pass