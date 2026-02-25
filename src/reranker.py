import os 
import numpy as np
from openai import OpenAI
from typing import List, Dict, Any

# 初始化 OpenAI 客户端
client = OpenAI()

def get_embedding(text: str, model="text-embedding-3-small"):
    """
    呼叫 OpenAI API 將純文字轉換為數學向量
    """
    if not text or not text.strip():
        # 若無有效文字，回傳 1536 維的零向量以防止計算錯誤
        return np.zeros(1536)
    
    # 移除換行符號以提升 Embedding 品質
    text = text.replace("\n", " ")
    response = client.embeddings.create(input=[text], model=model)
    return np.array(response.data[0].embedding)

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    計算兩個向量的餘弦相似度
    """
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)

    # 避免除以零的數學錯誤
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    
    return float(dot_product / (norm_v1 * norm_v2))

def rerank_videos(node_query: str, video_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    接收節點的查詢字串與 Youtube 影片清單（包含標題與描述）
    計算語意相似度後，為每部影片加上分數並重新排序
    """
    if not video_list:
        return []
    
    # 將節點的核心需求轉化為向量
    query_embedding = get_embedding(node_query)

    # 逐一計算候選影片的相似度分數
    for video in video_list:
        # 將影片的標題與描述合併，作為該影片的特徵文本
        video_text = f"{video.get('title', '')} {video.get('description', '')}"
        video_embedding = get_embedding(video_text)

        # 執行矩陣運算並將分數寫入字典中
        score = cosine_similarity(query_embedding, video_embedding)
        video['similarity_score'] = score

    # 根據相似度分數由高到低重新排序清單
    renked_videos = sorted(video_list, key=lambda x: x['similarity_score'], reverse=True)

    return renked_videos