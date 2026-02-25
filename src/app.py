import streamlit as st
import networkx as nx
import base64
import streamlit.components.v1 as components

from llm_engine import generate_learning_path
from graph_builder import build_and_validate_graph
from video_search import fetch_candidate_videos
from reranker import rerank_videos

@st.cache_data(show_spinner=False, ttl=86400) # 24 小時快取，避免頻繁呼叫 LLM API
def get_cached_learning_path(topic: str, language: str):
    """
    包裝 LLM 生成邏輯。相同的 topic 與 language 在 24 小時內只會消耗一次 API 額度
    """
    return generate_learning_path(topic, language)

@st.cache_data(show_spinner=False, ttl=86400) # 24 小時快取，避免頻繁呼叫 Graph 建構邏輯
def get_cached_videos(node_query: str, topic_name: str, language: str):
    """
    包裝 youtube 檢索與 OpenAI 重排序邏輯。相同的節點查詢將直接
    """
    candidates = fetch_candidate_videos(topic_name, language)
    if candidates:
        return rerank_videos(node_query, candidates)
    return []

# 根據 Graph 的拓樸結構，計算 Mermaid 圖表需要的動態高度
def calculate_graph_height(G: nx.DiGraph) -> int:
    if not G.nodes:
        return 300
    
    levels = {}
    for n, d in G.nodes(data=True):
        lvl = d.get('level', 0)
        levels[lvl] = levels.get(lvl, 0) + 1
    
    # 找出節點數量最多的那層
    max_nodes_in_single_level = max(levels.values())

    # 假設每個節點在垂直方向約占 80 像素，並加上 150 像素的基礎上下邊距
    calculated_height = (max_nodes_in_single_level * 80) + 150
    
    # 最少 300 像素，最高不超過 1000 像素
    return max(300, min(calculated_height, 1000))    

# 將 NetworkX 圖形物件轉譯為 Mermaid 的流程圖與法
# 採用 Top-Down 的排版
def convert_nx_to_mermaid(G: nx.DiGraph) -> str:
    mermaid_code = "graph LR\n"

    # 宣告所有節點及其顯示文字
    for node_id, node_data in G.nodes(data=True):
        # 處理名稱可能影響 Mermaid 語法的引號
        safe_name = node_data.get('topic_name', node_id).replace('"', "'")
        # 節點 ID ["顯示名稱"]
        mermaid_code += f'    {node_id}["{safe_name}"]\n'

    # 宣告所有依賴連線
    for source, target in G.edges():
        mermaid_code += f"    {source} --> {target}\n"

    
    return mermaid_code

# Streamlit 網頁介面建構

st.set_page_config(page_title="Learning Path Generator", layout="wide")

# 使用 session_state 確保重整畫面時資料不會遺失
if "graph_data" not in st.session_state:
    st.session_state.graph_data = None
if "mermaid_syntax" not in st.session_state:
    st.session_state.mermaid_syntax = None
if "language" not in st.session_state:
    st.session_state.language = "English"

# 語言選擇器放在最上方
language_choice = st.radio(
    "Language / 語言",
    options=["English", "繁體中文"],
    horizontal=True,
    key="language_selector"
)

st.session_state.language = language_choice

# 根據語言設定 UI 文字
if language_choice == "繁體中文":
    ui_text = {
        "title": "學習路徑生成器",
        "input_label": "輸入你想學習的領域",
        "input_placeholder": "例如：資料科學、網頁開發、機器學習",
        "button": "生成學習路徑",
        "warning": "請輸入有效的主題",
        "spinner": f"正在分析並生成學習路徑...",
        "error": "生成過程發生錯誤",
        "graph_title": "生成的學習路徑",
        "details_title": "節點詳細資訊",
        "level": "層級",
        "description": "描述",
        "estimated_hours": "預估時數",
        "hours": "小時",
        "key_concepts": "關鍵概念",
        "actionable_steps": "學習步驟",
        "no_description": "無描述",
        "find_videos": "尋找精選教學影片 🎬",
        "video_spinner": "正在檢索並使用 AI 進行語意重排序 (Reranking)...",
        "video_top3_title": "🏆 AI 精選 Top 3 教學資源",
        "video_rank_label": "第 {rank} 名：語意契合度 `{pct}%`",
        "video_not_found": "找不到適合的影片，或 YouTube API 發生錯誤。"
    }
else:
    ui_text = {
        "title": "Learning Path Generator",
        "input_label": "Enter a Learning Topic",
        "input_placeholder": "e.g., Data Science, Web Development, Machine Learning",
        "button": "Generate Learning Path",
        "warning": "Please enter a valid learning topic.",
        "spinner": f"Analyzing and generating learning path...",
        "error": "An error occurred while generating the learning path",
        "graph_title": "Generated Learning Path",
        "details_title": "Detailed Learning Nodes",
        "level": "Level",
        "description": "Description",
        "estimated_hours": "Estimated Hours",
        "hours": "hours",
        "key_concepts": "Key Concepts",
        "actionable_steps": "Actionable Steps",
        "no_description": "No description available",
        "find_videos": "Find Curated Tutorial Videos 🎬",
        "video_spinner": "Fetching candidates and reranking with AI semantics...",
        "video_top3_title": "🏆 AI Top 3 Recommended Learning Videos",
        "video_rank_label": "Rank #{rank}: Semantic Match `{pct}%`",
        "video_not_found": "No suitable videos found, or YouTube API request failed."
    }

st.title(ui_text["title"])

topic_input = st.text_input(ui_text["input_label"], placeholder=ui_text["input_placeholder"])

if st.button(ui_text["button"]):
    if not topic_input.strip():
        st.warning(ui_text["warning"])
    else:
        with st.spinner(ui_text["spinner"]):
            try:
                # 將選擇的語言作為參數傳遞給後端 API
                path_data = get_cached_learning_path(topic_input, language_choice)

                # 建構 NetworkX 圖形並驗證邏輯
                G, node_levels = build_and_validate_graph(path_data)

                # 轉譯為 Mermaid 語法
                mermaid_syntax = convert_nx_to_mermaid(G)

                # 將結果存入狀態中
                st.session_state.graph_data = G
                st.session_state.mermaid_syntax = mermaid_syntax
            except Exception as e:
                st.error(f"{ui_text['error']}: {e}")

# 渲染結果
if st.session_state.mermaid_syntax and st.session_state.graph_data:
    st.markdown(f"### {ui_text['graph_title']}")
    
    mermaid_code = st.session_state.mermaid_syntax
    
    # 1. 將語法編碼為 Base64，避免引號與換行符號破壞 HTML 結構
    b64_code = base64.b64encode(mermaid_code.encode("utf-8")).decode("utf-8")
    
    # 2. 建構客製化互動視窗的 HTML/JS 腳本 (修正套件載入錯誤與新增錯誤捕捉)
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
        <style>
            body {{ margin: 0; padding: 0; background-color: transparent; }}
            #container {{ width: 100vw; height: 100vh; overflow: hidden; }}
        </style>
    </head>
    <body>
        <div id="container"></div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            
            mermaid.initialize({{ startOnLoad: false, theme: 'default' }});
            
            try {{
                // 解碼 Base64 取得 Mermaid 語法
                const code = decodeURIComponent(escape(window.atob('{b64_code}')));
                
                mermaid.render('graphSvg', code).then((result) => {{
                    document.getElementById('container').innerHTML = result.svg;
                    const svgElement = document.querySelector('#container svg');
                    
                    // 強制讓 SVG 填滿我們設定的視窗大小並解除預設寬度限制
                    svgElement.style.width = '100%';
                    svgElement.style.height = '100%';
                    svgElement.style.maxWidth = 'none';
                    
                    // 呼叫全域的 svgPanZoom 函數來綁定放大縮小功能
                    window.svgPanZoom(svgElement, {{
                        zoomEnabled: true,
                        controlIconsEnabled: true,
                        fit: true,
                        center: true,
                        minZoom: 0.2,
                        maxZoom: 10
                    }});
                }}).catch(err => {{
                    document.getElementById('container').innerHTML = '<p style="color:red; padding:20px;">圖表渲染失敗: ' + err.message + '</p>';
                }});
            }} catch (err) {{
                document.getElementById('container').innerHTML = '<p style="color:red; padding:20px;">腳本執行錯誤: ' + err.message + '</p>';
            }}
        </script>
    </body>
    </html>
    """
    
    # 3. 渲染高度固定為 600px 的互動式視窗
    components.html(html_code, height=600, scrolling=False)

    # 依據 level 進行分組與排序顯示
    G = st.session_state.graph_data
    levels = {}
    for n, d in G.nodes(data=True):
        lvl = d.get('level', 0)
        if lvl not in levels:
            levels[lvl] = []
        levels[lvl].append((n, d))

    st.markdown(f"### {ui_text['details_title']}")
    # --- 下方維持原本的 for lvl in sorted(levels.keys()): 迴圈邏輯 ---
    # 透過層級排序，依序列出每個節點的具體學習內容

    for lvl in sorted(levels.keys()):
        st.subheader(f"{ui_text['level']} {lvl}")
        for node_id, data in levels[lvl]:
            with st.expander(f"{data.get('topic_name', node_id)}"):
                # 顯示節點的描述、核心概念、預估學習時間等資訊
                st.markdown(f"**{ui_text['description']}:** {data.get('description', ui_text['no_description'])}")
                est_hours = data.get('estimated_hours', 0)
                st.markdown(f"**{ui_text['estimated_hours']}:** {est_hours} {ui_text['hours']}")

                concepts = data.get('key_concepts', [])
                if concepts:
                    st.markdown(f"**{ui_text['key_concepts']}:** {', '.join(concepts)}")

                steps = data.get('actionable_steps', [])
                if steps:
                    st.markdown(f"**{ui_text['actionable_steps']}:**")
                    for step in steps:
                        st.markdown(f"- {step}")

                st.divider()
                if st.button(ui_text["find_videos"], key=f"btn_vid_{node_id}"):
                    with st.spinner(ui_text["video_spinner"]):
                        # 結合主題與詳細描述，讓 Embedding 具備更豐富的特徵
                        node_query = f"{data.get('topic_name', '')} {data.get('description', '')}"
                        # 取得前 10 名候選影片 Metadata
                        ranked_videos = get_cached_videos(node_query, data.get('topic_name', ''), language_choice)

                        if ranked_videos:
                            top_3_videos = ranked_videos[:3]
                            st.markdown("### AI-selected Top 3 teaching resources")

                            st.markdown(f"#### {ui_text['video_top3_title']}")
                            # 使用迴圈垂直渲染前三名影片與其分數
                            for index, vid in enumerate(top_3_videos, start=1):
                                score = vid.get('similarity_score', 0)
                                # 將分數轉換為易讀的百分比格式
                                match_percentage = round(score * 100, 1)
                                # 顯示排名與契合度
                                st.markdown(
                                    ui_text["video_rank_label"].format(
                                        rank=index,
                                        pct=match_percentage,
                                    )
                                )
                                st.video(f"https://www.youtube.com/watch?v={vid['id']}")
                        else:
                            st.warning(ui_text["video_not_found"])