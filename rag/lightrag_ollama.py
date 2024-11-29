import os
import logging
from lightrag import LightRAG, QueryParam
from lightrag.llm import ollama_model_complete, ollama_embedding
from lightrag.utils import EmbeddingFunc

BASE_DIR = "./rag/ragtest"
INPUT_DIR = "input"
OUTPUT_DIR = "output"
BOOK_NAME = "第二回-张翼德怒鞭督邮 何国舅谋诛宦竖"

WORKING_DIR = f"{BASE_DIR}/{OUTPUT_DIR}/{BOOK_NAME}"

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=ollama_model_complete,
    llm_model_name="qwen2.5:7b",
    llm_model_max_async=4,
    llm_model_max_token_size=32768,
    llm_model_kwargs={"host": "http://localhost:11434", "options": {"num_ctx": 32768}},
    embedding_func=EmbeddingFunc(
        embedding_dim=768,
        max_token_size=8192,
        func=lambda texts: ollama_embedding(
            texts, embed_model="nomic-embed-text", host="http://localhost:11434"
        ),
    ),
)

with open(f"{BASE_DIR}/{INPUT_DIR}/{BOOK_NAME}.txt", "r", encoding="utf-8") as f:
    rag.insert(f.read())

# Perform naive search
# print(
#     rag.query("这个故事的主要主题是什么？", param=QueryParam(mode="naive"))
# )

# # Perform local search
# print(
#     rag.query("这个故事的主要主题是什么？", param=QueryParam(mode="local"))
# )

# # Perform global search
# print(
#     rag.query("这个故事的主要主题是什么？", param=QueryParam(mode="global"))
# )

# Perform hybrid search
# print(
#     rag.query("这个故事的主要主题是什么？", param=QueryParam(mode="hybrid"))
# )
ans = rag.query("刘备和刘玄德什么关系？", param=QueryParam(mode="global"))
print(ans)
