from skills.code_review import CodeReviewSkill

# maps skill name (state["skill"]) to its instance
SKILL_REGISTRY={
    "code":CodeReviewSkill(),
}

def get_skill(skill_name: str):
    # looks up the active skill, raises clearly if an unknown name is passed
    skill=SKILL_REGISTRY.get(skill_name)
    if skill is None:
        raise ValueError(f"Unknown skill:{skill_name}")
    
    return skill