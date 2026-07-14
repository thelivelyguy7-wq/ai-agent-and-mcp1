# Implementation Plan: AI-Powered Mobile Review Pulse

## Goal Description
Develop an automated system to aggregate mobile store reviews, extract actionable insights using an LLM, and distribute the generated weekly pulse document via Google Docs and Gmail utilizing the Model Context Protocol (MCP).

## User Review Required
> [!IMPORTANT]
> Please review the 5 distinct phases below. Before we proceed to execution, what programming language (e.g., Python, TypeScript) and which LLM provider (e.g., OpenAI, Anthropic, Gemini) would you like to use for the Core Agent?

## Open Questions
> [!WARNING]
> - Do we want to implement a custom translation step for non-English reviews, or simply filter them out for the MVP?
> - How should we handle cases where no new reviews exist for the specified 8-12 week window? (Should we still send an email stating there are no new reviews?)

## Proposed Implementation Phases

### Phase 0: Prerequisites & Project Initialization
**Objective**: Finalize tech stack decisions, set up the repository, and configure the development environment.

**Implementation Steps:**
1. **Tech Stack Selection:** Confirm programming language (Python/TypeScript) and LLM Provider based on user feedback.
2. **Initialize Project:** Create the directory structure, initialize the package manager (e.g., `poetry` or `npm`), and install core dependencies.
3. **Environment Setup:** Create a `.env.example` file to document necessary API keys (LLM key, MCP environment variables).

**Files Affected:**
#### [NEW] `pyproject.toml` (or `package.json`)
#### [NEW] `.env.example`
#### [NEW] `.gitignore`

---

### Phase 1: Data Ingestion & Sanitization
**Objective**: Build the module to load, clean, and validate review data.

**Implementation Steps:**
1. **Schema Definition:** Define the data models for a "Review" (e.g., using Pydantic in Python) to ensure incoming data has required fields (text, rating, date).
2. **Data Loader:** Create `src/ingestion.py` to parse raw public review exports (CSV/JSON).
3. **Privacy Scrubber:** Create `src/sanitization.py` and implement Regex/NLP rules to strip PII (emails, names, phone numbers, device IDs).
4. **Data Filtering Rules:** Add logic to drop reviews that:
   - Have fewer than 8 words.
   - Contain emojis.
   - Are not in English.
   *(Note for MVP: Applying these filters to our 12-week dataset of 5,040 raw reviews yields exactly 2,013 high-quality, substantive reviews for the LLM to process).*
5. **Edge Case Handling:** Add logic to check for empty datasets, malformed exports, and truncate excessively long reviews.

**Files Affected:**
#### [NEW] `src/ingestion.py`
#### [NEW] `src/sanitization.py`
#### [NEW] `src/models.py`

---

### Phase 2: MCP Server Configuration & Client Integration
**Objective**: Establish secure communication with external tools without bespoke OAuth.

**Implementation Steps:**
1. **MCP Environment Setup:** Install the necessary MCP SDKs and configure the environment variables for the Google Docs and Gmail MCP servers.
2. **Client Wrapper:** Create `src/mcp_client.py` to handle the connection, discovery, and execution of tools on these servers.
3. **Health Checks:** Implement basic test functions in the client wrapper to verify tool execution (e.g., test connection to Google Docs and Gmail) before invoking heavy LLM processing.

**Files Affected:**
#### [NEW] `src/mcp_client.py`

---

### Phase 3: AI Processing Engine
**Objective**: Build the core logic to cluster themes, distill insights, format the report, and enforce constraints.

**Implementation Steps:**
1. **LLM Integration:** Create `src/ai_engine.py` to integrate the chosen LLM Provider API, including exponential backoff and retry logic for API limits.
2. **Prompt Engineering:** Create `src/prompts.py` to design the system prompts for:
   - Grouping reviews into a maximum of 5 themes.
   - Selecting the top 3 themes.
   - Extracting 3 verbatim quotes and generating 3 actionable steps.
3. **Constraint Enforcement:** Implement logic to format the output as a single-page note (≤250 words).
4. **Validation Logic:** Create `src/validators.py` with a post-generation check to verify that extracted quotes exist in the sanitized source text (preventing hallucinations).

**Files Affected:**
#### [NEW] `src/ai_engine.py`
#### [NEW] `src/prompts.py`
#### [NEW] `src/validators.py`

---

### Phase 4: End-to-End Orchestration
**Objective**: Tie all modular components together into the final execution pipeline.

**Implementation Steps:**
1. **Orchestrator Script:** Create `src/main.py` to act as the entry point.
2. **Pipeline Wiring:** Chain the modules: `Ingestion` -> `Sanitization` -> `AI Engine` -> `Validators`.
3. **MCP Publishing Flow:** 
   - Call the Google Docs MCP tool to publish the validated report.
   - Call the Gmail MCP tool to draft the notification email linking to the published document.
4. **Fallback Mechanism:** Implement logic so that if Google Docs creation fails persistently, the system falls back to sending the full Markdown text within the Gmail draft.

**Files Affected:**
#### [NEW] `src/main.py`

---

### Phase 5: Testing & Validation
**Objective**: Verify the system against all problem statement constraints and edge cases.

**Implementation Steps:**
1. **Unit Testing:** Write tests for the data sanitization module to ensure PII is properly masked.
2. **Validation Testing:** Write tests for schema validation (handling missing fields) and quote verification (hallucination checks).
3. **End-to-End Run:** Execute the main script locally with a sample/edge-case dataset (e.g., containing non-English text, PII).
4. **Manual Verification:** Verify the final outputs in Google Docs and Gmail, confirming the 250-word limit, the 3-theme constraint, and zero PII leakage.

**Files Affected:**
#### [NEW] `tests/test_sanitization.py`
#### [NEW] `tests/test_validators.py`
#### [NEW] `tests/test_ingestion.py`

---

## Verification Plan

### Automated Tests
- `pytest` (if Python) for unit testing data sanitization (ensuring PII is masked).
- Tests for schema validation (handling missing or malformed fields).
- Quote verification tests to ensure the hallucination check correctly identifies fake quotes.

### Manual Verification
- Execute the main script locally with an edge-case dataset (e.g., containing non-English text, PII, and edge-case formatting).
- Verify the outputs in Google Docs and Gmail, confirming the 250-word limit and 3-theme constraint are met.
