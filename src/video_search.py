import os
import urllib.parse
import urllib.request
import json
from typing import List, Dict, Any

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def fetch_candidate_videos(topic_name: str, language: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    向 YOUTUBE API 請求多部相關教學影片的 Metadata 
    回傳包含影片 ID、標題與描述的字典清單
    """
    if not YOUTUBE_API_KEY:
        print("Error: YOUTUBE_API_KEY is not set.")
        return []
    
    # 組合精準的搜尋關鍵字  
    search_intent = "教學" if language ==  "繁體中文" else "tutorial"
    query = f"{topic_name} {search_intent}"
    encoded_query = urllib.parse.quote(query)

    # 擴大 maxResults 已取得足夠的候選影片供後續重排序
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults={max_results}&q={encoded_query}&type=video&key={YOUTUBE_API_KEY}"

    candidates = []
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())

            items = result.get("items", [])
            for item in items:
                video_id = item["id"].get("videoId")
                snippet = item.get("snippet", {})
                title = snippet.get("title", "")
                description = snippet.get("description", "")

                # 將可用於語意比對的特徵打包為字典
                if video_id:
                    candidates.append({
                        "id": video_id,
                        "title": title,
                        "description": description
                    })
        return candidates
    except Exception as e:
        print(f"Error fetching videos: {e}")
        return []
