import os
from dotenv import load_dotenv
from openai import OpenAI

from schema import LearningPath

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 接收學習主題，呼叫 LLM 並強制輸出符合 LearningPath 結構的資料
def generate_learning_path(topic: str, language: str) -> LearningPath:
    prompt = f"""
    You are a senior curriculum planner and subject-matter expert.
    Please design a beginner-to-advanced learning path for the topic "{topic}".
    
    Strict requirements:
    1. Break this domain into 10 to 15 core learning nodes.
    2. Each node must have clear prerequisite dependencies.
    3. Dependencies must form a Directed Acyclic Graph (DAG), with absolutely no circular dependencies (e.g., A depends on B and B depends on A).
    4. Foundational starting nodes that require no prior knowledge must have an empty prerequisites array.
    
    Language & Formatting Rules:
    5. OUTPUT LANGUAGE: All display fields (topic_name, description, key_concepts, actionable_steps) MUST be written in {language}.
    6. SYSTEM ID STRICT RULE: The 'id' field MUST ALWAYS remain in English lowercase snake_case, regardless of the {language} chosen. This is critical for system stability.
    """

    try:
        # 使用 parse 方法強制進行結構化輸出
        response = client.beta.chat.completions.parse(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are a precise learning-path generation engine. You must only output data that conforms to the specified JSON Schema."},
                {"role": "user", "content": prompt}
            ],
            response_format=LearningPath,
        )

        # 提取並回傳已被 Pydantic 解析並驗證過的物件
        parsed_path = response.choices[0].message.parsed
        return parsed_path
    
    except Exception as e:
        print(f"Error generating learning path: {e}")
        raise