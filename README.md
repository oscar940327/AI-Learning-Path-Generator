# AI-Learning-Path-Generator: Dynamic Learning Path & AI Reranking Engine

AI-Learning-Path-Generator is an AI-driven educational tool that dynamically generates structured learning paths for any given topic. Instead of returning a flat checklist, it builds a **Directed Acyclic Graph (DAG)** of learning nodes and recommends high-quality tutorial videos through semantic reranking.

AI-Learning-Path-Generator 是一個 AI 驅動的學習工具，能針對任意主題動態生成結構化學習路徑。它不只提供平面清單，而是建立具備先後依賴的 **有向無環圖（DAG）**，並透過語意重排序推薦更貼近需求的教學影片。

## Key Features / 核心功能

- **Deterministic LLM Output via Pydantic**: Enforces structured outputs from the LLM (GPT-5.2) and parses them into reliable Python objects.
- **以 Pydantic 強制結構化輸出**：限制 LLM（GPT-5.2）輸出符合資料模型，降低格式漂移與解析失敗風險。

- **Graph-Based Dependency Resolution**: Uses `NetworkX` to model learning milestones as a DAG, performs topological sorting, and handles cycle breaking.
- **圖論依賴解析**：使用 `NetworkX` 建立學習節點 DAG、進行拓樸排序，並在必要時自動打破循環依賴。

- **Semantic Video Reranking**: Retrieves candidate videos from YouTube Data API, embeds query/video texts with `text-embedding-3-small`, and reranks via cosine similarity.
- **語意影片重排序**：先用 YouTube Data API 取得候選影片，再以 `text-embedding-3-small` 與餘弦相似度計算語意匹配分數。

- **Interactive Topology Visualization**: Renders Mermaid SVG inside Streamlit with pan/zoom support via `svg-pan-zoom`.
- **互動式拓樸視覺化**：在 Streamlit 中渲染 Mermaid 圖並整合 `svg-pan-zoom`，支援拖曳與縮放。

## Tech Stack / 技術棧

- **Backend & Logic / 後端與邏輯**: Python 3, NetworkX, Pydantic, NumPy
- **AI & Search / AI 與檢索**: OpenAI API (Chat + Embeddings), YouTube Data API v3
- **Frontend / 前端**: Streamlit, Mermaid.js, svg-pan-zoom

## Installation & Setup / 安裝與設定

### 1) Clone Repository / 下載專案

```bash
https://github.com/oscar940327/AI-Learning-Path-Generator.git
cd AI-Learning-Path-Generator
```

### 2) Install Dependencies / 安裝套件

It is recommended to use a virtual environment.
建議先建立並啟用虛擬環境。

```bash
pip install -r requirements.txt
```

### 3) Environment Variables / 設定環境變數

Create a `.env` file in the project root:
在專案根目錄建立 `.env` 檔案：

```env
OPENAI_API_KEY="sk-your-openai-api-key"
YOUTUBE_API_KEY="your-youtube-data-api-key"
```

## Usage / 使用方式

Run the Streamlit app locally:
在本機啟動 Streamlit：

```bash
streamlit run src/app.py
```

Then open `http://localhost:8501` in your browser.
接著在瀏覽器開啟 `http://localhost:8501`。

## System Architecture / 系統架構

1. **Input Layer / 輸入層**
   - User enters a topic and selects UI language.
   - 使用者輸入主題並選擇介面語言。

2. **LLM Engine (`src/llm_engine.py`)**
   - Generates 10–15 learning nodes with prerequisites using structured output.
   - 使用結構化輸出產生 10–15 個帶有前置條件的學習節點。

3. **Graph Builder (`src/graph_builder.py`)**
   - Builds/validates the DAG, removes cyclic edges if needed, and computes node levels.
   - 建立並驗證 DAG，必要時移除循環邊，並計算節點層級。

4. **UI & Visualization (`src/app.py`)**
   - Converts graph data to Mermaid syntax and renders an interactive graph in Streamlit.
   - 將圖資料轉為 Mermaid 語法，並在 Streamlit 中以互動方式呈現。

5. **Retrieval & Reranking (`src/video_search.py`, `src/reranker.py`)**
   - Fetches top candidates from YouTube and reranks them by semantic similarity.
   - 從 YouTube 取得候選影片後，依語意相似度重排序。

## 📌 Notes / 備註

- This project depends on external APIs (OpenAI, YouTube). Ensure keys are valid and quotas are available.
- 本專案依賴外部 API（OpenAI、YouTube），請確認金鑰有效且配額可用。

- If API calls fail, check `.env`, network access, and API usage limits first.
- 若 API 呼叫失敗，請優先檢查 `.env`、網路連線與 API 配額限制。