# Self-Reviewing Model

A sophisticated agentic system that generates, validates, and iteratively refines responses through automated fact-checking and critique cycles. The system leverages multiple LLMs to ensure high-quality, accurate output through an intelligent feedback loop.

## Overview

The Self-Reviewing Model is a multi-agent framework that combines:
- **Local LLM Generation**: Uses Ollama (Llama 3.2) for draft creation and refinement
- **Cloud-Based Validation**: Uses Groq API (Llama 3.1) for fact-checking and critiquing
- **Iterative Refinement**: Automatically improves responses based on feedback until quality threshold is met
- **State Management**: Maintains context throughout the refinement pipeline using LangGraph

## Architecture

### Workflow Pipeline

```
User Input
    ↓
[Generate] → Draft generated using local LLM
    ↓
[Fact-Check] → Validates factual accuracy using Groq
    ↓
[Critique] → Evaluates clarity, completeness, quality
    ↓
    ├─→ Score ≥ 7.0 OR Max Iterations? → [Finalize] → Output
    │
    └─→ Otherwise → [Refine] → Back to Fact-Check
```

### Key Components

#### 1. **Generate Node** (`nodes/generate.py`)
- Creates initial draft response using local Ollama model (Llama 3.2)
- Temperature: 0.7 for balanced creativity
- Increments iteration counter

#### 2. **Fact-Check Node** (`nodes/fact_check.py`)
- Validates factual accuracy of the draft
- Uses Groq API with structured JSON output
- Returns:
  - `is_accurate`: Boolean indicating overall accuracy
  - `flagged_claims`: List of potentially incorrect claims
  - `corrections`: Suggested corrections for flagged claims

#### 3. **Critique Node** (`nodes/critique.py`)
- Evaluates draft quality on multiple dimensions:
  - Clarity and readability
  - Completeness in addressing the request
  - Factual correctness (informed by fact-check results)
- Returns structured feedback:
  - `strengths`: What the draft does well
  - `weaknesses`: Areas for improvement
  - `suggestions`: Specific actionable improvements
  - `score`: Quality score (0-10 scale)

#### 4. **Refine Node** (`nodes/refine.py`)
- Takes critique feedback and incorporates improvements
- Uses local Ollama model for refinement
- Preserves strengths while fixing identified weaknesses
- Corrects factual errors identified in fact-check phase
- Loops back to fact-check for validation

#### 5. **Finalize Node** (`nodes/finalize.py`)
- Outputs the final response
- Triggered when either:
  - Quality score ≥ 7.0 (threshold met)
  - Maximum iterations (3) reached

### State Schema (`state/schema.py`)

The system maintains a `AgentState` TypedDict with:
- `user_input`: Original user request
- `draft`: Current draft response
- `fact_check`: Fact-checking results
- `critique`: Quality critique and score
- `score`: Current quality score
- `iteration`: Current iteration count
- `max_iterations`: Maximum iterations allowed (default: 3)
- `final_output`: Final response

## Project Structure

```
Self-Reviewing-Model/
├── main.py                 # Entry point - runs the pipeline
├── refine_test.py          # Testing utilities for refinement
├── requirements.txt        # Python dependencies
├── config/
│   └── settings.py         # Configuration (API keys, thresholds, models)
├── graph/
│   ├── builder.py          # LangGraph pipeline construction
│   ├── diagram.md          # Workflow visualization
│   └── visualize.py        # Graph visualization utilities
├── nodes/
│   ├── generate.py         # Draft generation node
│   ├── fact_check.py       # Fact validation node
│   ├── critique.py         # Quality assessment node
│   ├── refine.py           # Refinement node
│   └── finalize.py         # Output finalization node
├── prompts/                # Prompt templates (if needed)
├── state/
│   └── schema.py           # State management schema
└── README.md               # This file
```

### External Services

1. **Ollama (Local)**
   - Model: Llama 3.2
   - Used for: Draft generation and refinement
   - No API key required (runs locally)
   - Download: https://ollama.ai

2. **Groq API (Cloud)**
   - Model: Llama 3.1 8B Instant
   - Used for: Fact-checking and critiquing
   - Requires API key: https://console.groq.com

## Usage

### Basic Usage

Run the pipeline with a user query:

```bash
python main.py
```

This will run the default query: `"Explain how transformer work"`

### Programmatic Usage

```python
from main import run

# Run with custom input
run("What is machine learning?")
```
## How It Works

### Execution Flow

1. **Initialization**: System receives user input and initializes state
2. **Generation**: Local LLM generates initial draft response
3. **Validation Loop**:
   - Fact-check the draft for accuracy
   - Critique the draft for quality
   - Evaluate completion criteria:
     - **Finalize** if score ≥ 7.0 (quality threshold met)
     - **Finalize** if iterations ≥ max_iterations
     - **Refine** otherwise, then return to validation
4. **Output**: Return final polished response with score

### Quality Scoring

Scores are on a 0-10 scale based on:
- **Clarity**: How well-written and understandable
- **Completeness**: Whether all aspects are addressed
- **Accuracy**: Freedom from factual errors
- **Relevance**: How well it matches the request

The system stops refining when the score reaches 7.0 or higher, indicating good quality.

### Visualization

Generate a visualization of the workflow graph:

```bash
python -m graph.visualize
```

This creates a diagram showing the node flow and decision paths.

## Performance Considerations

- **Local Model**: Ollama (Llama 3.2) is fast but may be less accurate for complex reasoning
- **Cloud Model**: Groq (Llama 3.1) is more accurate but requires API calls
- **Iterations**: More iterations = better quality but higher latency and cost
- **Typical Runtime**: 30-90 seconds per query (depending on complexity)
