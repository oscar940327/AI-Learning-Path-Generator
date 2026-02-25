from pydantic import BaseModel, Field
from typing import List

class LearningNode(BaseModel):
    id: str = Field(
        ..., 
        description="Unique identifier of the node. Must be lowercase snake_case, e.g., 'calculus', 'linear_algebra'"
    )
    topic_name: str = Field(
        ..., 
        description="Display name of the learning topic, e.g., 'Calculus', 'Linear Algebra'"
    )
    description: str = Field(
        ..., 
        description="Short summary of the core concepts and learning objectives of this topic"
    )
    estimated_hours: int = Field(
        ..., 
        description="Estimated number of hours required to complete this learning node"
    )
    key_concepts: List[str] = Field(
        default_factory=list,
        description="List of key concepts or skills that will be learned in this node"
    )
    actionable_steps: List[str] = Field(
        default_factory=list,
        description="List of actionable steps or learning tasks to complete this topic"
    )
    prerequisites: List[str] = Field(
        default_factory=list, 
        description="List of prerequisite node IDs that must be completed before this topic. Empty if this is a starting node"
    )

class LearningPath(BaseModel):
    nodes: List[LearningNode] = Field(
        ..., 
        description="List of all nodes that make up the complete learning path"
    )