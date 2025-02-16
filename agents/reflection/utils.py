
from agents.prompts import REFLECTIONS_PROMPT, UPDATE_RULES_PROMPT
from agents.reflection.state import ReflectionState
from agents.reflection.configuration import ReflectionConfiguration

async def build_reflection_prompt(
    state: ReflectionState,
    config: ReflectionConfiguration,
) -> str:
    """Build the reflection prompt."""
    
    editor_feedback = state.editor_feedback["content"] if state.editor_feedback and "content" in state.editor_feedback else ""
    return REFLECTIONS_PROMPT.format(
        original_text=state.original_text,
        revised_text=state.revised_text,
        editor_feedback=editor_feedback,
    ) 

async def build_update_rules_prompt(
    new_rules: list[str],
    existing_rules: list[str],
) -> str:
    """Build the update rules prompt."""
    new_rules_string = "\n".join(new_rules)
    existing_rules_string = "\n".join(existing_rules)
    return UPDATE_RULES_PROMPT.format(
        existing_rules=existing_rules_string,
        new_rules=new_rules_string,
    ) 
