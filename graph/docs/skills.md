# Skills Architecture
 
This document covers the design and implementation of the **skills system** added to the self-reviewing agent — a strategy pattern that lets the same LangGraph pipeline apply domain-specific review logic (currently: general writing review and code review) without duplicating the graph itself.
 
## Motivation
 
The original pipeline (`generate → fact_check → critique → refine → finalize`) used one fixed prompt per node, tuned for general writing review (strengths / weaknesses / suggestions). Code review needs fundamentally different evaluation criteria — bugs and edge cases instead of weaknesses, correctness instead of clarity — so a single hardcoded critique shape doesn't generalize.
 
Rather than branching with if/else inside existing nodes, the system introduces a **skill interface**: each skill owns its own prompt logic and, where needed, its own critique node and result shape. The graph routes between them based on a single `state["skill"]` field.
 
## Package Structure
 
```
skills/
├── base.py            # BaseSkill — abstract interface every skill must implement
├── registry.py         # SKILL_REGISTRY — name -> skill instance lookup
└── code_review.py      # CodeReviewSkill — concrete implementation
```
 
`fact_check_node` and `generate_node` remain skill-agnostic for now; only critique and refine logic currently differ by skill.
 
## The `BaseSkill` Interface
 
```python
class BaseSkill(ABC):
    name: str
 
    @abstractmethod
    def build_generate_prompt(self, user_input: str) -> str: ...
 
    @abstractmethod
    def build_critique_prompt(self, user_input: str, draft: str, fact_check_summary: str) -> str: ...
 
    @abstractmethod
    def build_refine_prompt(self, user_input: str, draft: str, critique: dict, correction_notes: str) -> str: ...
```
 
Using `ABC` + `@abstractmethod` means a skill missing any of these three methods fails at **instantiation time**, not at runtime mid-conversation. This was a deliberate choice to catch incomplete skill implementations early.
 
`fact_check` is intentionally excluded from the interface — accuracy checking is treated as skill-independent and stays handled by the existing shared `fact_check_node`.
 
## State Changes
 
```python
class CodeReviewResult(TypedDict):
    strengths: list[str]
    bugs: list[str]          # replaces "weaknesses" for code-specific framing
    suggestions: list[str]
    score: float
 
class AgentState(TypedDict):
    ...
    skill: str                                          # "general" (default) or "code"
    critique: Optional[Union[Critique, CodeReviewResult]]  # shape depends on active skill
    score: float                                         # flat, regardless of critique shape
    ...
```
 
`score` is deliberately kept flat at the top level of state, independent of which critique shape produced it. This is what allows routing logic (`should_continue`) to remain completely unaware of skill type — it only ever reads `state["score"]`.
 
## Graph Changes
 
A new conditional edge, `route_critique`, sits after `fact_check` and reads `state["skill"]` to decide which critique node receives the draft:
 
```python
def route_critique(state: AgentState) -> str:
    if state["skill"] == "code":
        return "critique_code"
    return "critique"
```
 
Both critique nodes (`critique_node`, `critique_code_node`) converge back into the same `should_continue` router after passing through a new `track_best_node` (see below). This means the loop-control logic, max-iteration cap, and finalize path are all shared infrastructure — only the evaluation step itself diverges by skill.
 
```
generate → fact_check → route_critique ─┬─ critique ──────┐
                                          └─ critique_code ─┤
                                                             ▼
                                                       track_best
                                                             │
                                                      should_continue
                                                       ↙           ↘
                                                  refine         finalize → END
                                                     │
                                                     └──→ fact_check (loop)
```
 
On every loop iteration, `refine → fact_check` re-runs fact-checking before the draft is re-routed through `route_critique` again. Since `state["skill"]` never changes mid-run, a code-review run will always loop back through `critique_code`, never accidentally falling into the general path.
 
## `nodes/critique_code.py`
 
Mirrors the structure of `critique_node`, but:
- Pulls its prompt from `CodeReviewSkill.build_critique_prompt()` via the registry, instead of an inline f-string
- Targets the `CodeReviewResult` shape (`bugs` instead of `weaknesses`)
- Uses the same `json_mode` + defensive-unwrap + `setdefault()` safety pattern established for `critique_node` and `fact_check_node`, to handle cases where the Groq model wraps its JSON output under an extra key or omits a field
## `nodes/refine.py` — Skill-Aware Branching
 
`refine_node` branches once on `state["skill"]`:
 
- **`code`** — delegates entirely to `CodeReviewSkill.build_refine_prompt()`, which reads `critique["bugs"]`
- **`general`** (default) — keeps its original inline prompt unchanged, reading `critique["weaknesses"]`
This keeps the skill abstraction honest: prompt-building logic for the code skill lives entirely inside `CodeReviewSkill`, not leaked into the node itself via key-checking or duck-typing.
 
## Best-Draft Tracking
 
### Problem Found During Testing
 
Forcing a refine loop (by temporarily raising `SCORE_THRESHOLD` above what the critic was scoring) surfaced a real failure mode: the refiner does not monotonically improve the draft. In one test run:
 
| Iteration | Score | Notes |
|---|---|---|
| 1 | 8.0 | clean |
| 2 | 8.0 | clean |
| 3 | 6.0 | refine introduced a new logic bug, caught by fact_check on the next pass |
 
Because `max_iterations` forces a finalize regardless of score trend, the pipeline was returning iteration 3's regressed draft instead of the better iteration 1/2 result.
 
### Fix — `track_best_node`
 
A new node runs after every critique (both skill paths) and records the highest-scoring draft seen so far:
 
```python
def track_best_node(state: AgentState) -> dict:
    current_score = state["score"]
    best_score = state.get("best_score", 0.0)
 
    if current_score > best_score:
        return {"best_draft": state["draft"], "best_score": current_score}
 
    return {}  # no change — best_draft/best_score remain as-is
```
 
Returning `{}` when the current draft doesn't beat the existing best relies on LangGraph's merge behavior — a node only overwrites keys it explicitly returns, so omitting `best_draft`/`best_score` leaves them untouched in state.
 
`finalize_node` was updated to return `state["best_draft"]` instead of `state["draft"]`, so the final output is always the best-scoring version seen across the whole run, not simply whatever the last iteration happened to produce.
 
New state fields added to support this: `best_draft: Optional[str]`, `best_score: float` (both initialized in `main.py`'s `initial_state`).
 
## Known Issue Resolved During Testing — Token Limits
 
Longer drafts (post-refinement) occasionally produced critique responses that were truncated mid-JSON by Groq, raising `json_validate_failed` with `"max completion tokens reached before generating a valid document"`. Fixed by explicitly setting `max_tokens=1024` on all three `ChatGroq` clients (`fact_check_node`, `critique_node`, `critique_code_node`), since none had an explicit limit set and were relying on a default that proved insufficient as draft length grew across refine cycles.
 
## Verified Test Coverage
 
| Path | Status |
|---|---|
| General skill — happy path | Verified |
| Code skill — happy path | Verified |
| Refine loop — code skill, multi-iteration | Verified (surfaced the best-draft regression issue above) |
| `route_critique` skill switching | Verified |
| `track_best_node` correctly ignoring lower-scoring drafts | Verified |
| Refine loop — general skill | Not yet explicitly re-tested after best-draft changes |