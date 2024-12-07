from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma

embedding = SentenceTransformerEmbeddings(model_name="./models/all-MiniLM-L6-v2")

def retriever_query(documents, query, n_results=250, w=0.5):
    bm25_retriever = BM25Retriever.from_texts(documents)
    bm25_retriever.k = n_results

    chroma_db = Chroma.from_texts(documents, embedding=embedding)
    chroma_retriever = chroma_db.as_retriever(search_kwargs={"k": n_results})

    ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, chroma_retriever], weights=[w, 1-w])
    result = ensemble_retriever.get_relevant_documents(query)
    chroma_db.delete_collection()
    return [doc.page_content for doc in result][:n_results]

if __name__ == "__main__":
    pass