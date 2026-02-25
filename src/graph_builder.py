import networkx as nx
from typing import Dict, Tuple

from schema import LearningPath

# 將 LLM 輸出的租料建立為 DiGraph 
def build_and_validate_graph(path_data: LearningPath) -> Tuple[nx.DiGraph, Dict[str, int]]:
    G = nx.DiGraph()

    # 初始化圖形
    for node in path_data.nodes:
        G.add_node(
            node.id,
            topic_name=node.topic_name,
            description=node.description,
            key_concepts=node.key_concepts,
            estimated_hours=node.estimated_hours,
            actionable_steps=node.actionable_steps
        )

    # 建立有向邊，定義學習先後順序
    # prerequisite -> node.id
    for node in path_data.nodes:
        for prereq in node.prerequisites:
            # 確保前置節點存在於我們定義的節點清單中
            if prereq in G.nodes:
                G.add_edge(prereq, node.id)

    # 系統防禦：循環依賴偵測與破壞
    # 如果 LLM 產生了 A->B->C->A 的結構，這將無法進行拓墣
    if not nx.is_directed_acyclic_graph(G):
        try:
            # 找出途中所有的循環結構
            cycles = list(nx.simple_cycles(G))
            for cycle in cycles:
                # cycle 是一個節點 ID 的列表，例如 ['A', 'B', 'C']
                # 強制移除最後一個節點連回第一個節點的邊 ('C' -> 'A') 以打破循環
                if len(cycle) >= 2 and G.has_edge(cycle[-1], cycle[0]):
                    G.remove_edge(cycle[-1], cycle[0])
        except Exception as e:
            pass # 預防性捕捉例外

    # 拓譜排序與層級計算
    # 決定哪些是基礎知識，哪些是進階應用
    node_levels =  {}

    # nx.topological_sort 保證我們會先處理完所有的前置節點
    for node_id in nx.topological_sort(G):
        predecessors = list(G.predecessors(node_id))
        if not predecessors:
            node_levels[node_id] = 0 # 沒有前置節點，層級為 0
        else:
            # 當前節點的深度 = 所有前置節點中深度最大者 + 1
            node_levels[node_id] = max(node_levels[p] for p in predecessors) + 1
        
        G.nodes[node_id]['level'] = node_levels[node_id]

    return G, node_levels
    