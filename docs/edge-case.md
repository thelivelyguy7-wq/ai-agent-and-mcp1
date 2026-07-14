# Edge Cases and Corner Scenarios: AI-Powered Mobile Review Pulse

This document outlines potential edge cases, failure modes, and corner scenarios for the AI-Powered Mobile Review Pulse system, along with strategies for handling them.

## 1. Data Ingestion & Sanitization

| Edge Case | Description | Mitigation Strategy |
| :--- | :--- | :--- |
| **Empty Dataset** | No reviews exist for the specified 8–12 week window. | The system should detect this early, halt processing, and send a fallback email notifying stakeholders that no new data was found for the period. |
| **Malformed Export Files** | The CSV/JSON export is missing required fields (e.g., text, rating) or has an unexpected schema. | Implement strict schema validation (e.g., using Pydantic). If essential fields are missing, log an error and abort. If non-essential fields are missing, provide default values. |
| **Non-English Reviews** | The export contains reviews in unsupported languages. | Integrate a language detection step. Either filter out non-English reviews or add a translation preprocessing step before feeding to the LLM. |
| **Extremely Long Reviews** | A review exceeds typical lengths, potentially causing LLM context window truncation. | Truncate individual reviews to a reasonable character limit during the ingestion phase, preserving the start of the review where the core issue is usually stated. |
| **Obfuscated PII** | Users use creative formatting (e.g., "my email is john dot doe at gmail") that bypasses standard regex scrubbers. | Use an AI-based or advanced Named Entity Recognition (NER) scrubber in addition to regex, or instruct the core LLM to explicitly ignore/redact remaining PII it encounters. |

## 2. AI Processing Engine (LLM)

| Edge Case | Description | Mitigation Strategy |
| :--- | :--- | :--- |
| **LLM Hallucinations (Fake Quotes)** | The LLM generates "verbatim" quotes that do not exist in the source data. | Implement a post-generation validation step that performs string matching of the extracted quotes against the raw sanitized input. If a quote is not found, prompt the LLM to retry or drop the quote. |
| **Output Constraint Violation** | The LLM exceeds the 250-word limit or returns data in the wrong format. | Use strict system prompts with few-shot examples. Implement programmatic checks on the output length. If it fails, trigger a retry with a stronger constraint prompt. |
| **Insufficient Themes** | The data only supports 1 or 2 distinct themes instead of the requested top 3. | The prompt should explicitly instruct the LLM to output *up to* 3 themes. The parsing logic must gracefully handle cases where fewer than 3 themes are returned without failing. |
| **Toxic or Inappropriate Content** | User reviews contain profanity or hate speech which the LLM might amplify or include in the final report. | Implement a toxicity filter during the sanitization phase or instruct the LLM to filter out abusive reviews from the summary and quotes. |
| **API Limits & Timeouts** | The LLM provider API times out or hits a rate limit (HTTP 429). | Implement exponential backoff and retry logic in the LLM API client wrapper. |

## 3. MCP Integration (Google Docs & Gmail)

| Edge Case | Description | Mitigation Strategy |
| :--- | :--- | :--- |
| **MCP Server Unreachable** | The local or remote MCP server for Docs or Gmail is down. | The orchestrator should perform a health check on the MCP servers before initiating the expensive LLM processing. Fail fast and log the error. |
| **Google Docs Creation Failure** | The Google Docs tool call fails due to permissions, quota, or network issues. | Retry the operation. If it persistently fails, the orchestrator should fall back to saving the markdown locally and attempting to send the full text via Gmail instead of a link. |
| **Gmail Draft Failure** | The Gmail tool call fails (e.g., due to an invalid recipient list). | Validate email addresses before calling the MCP tool. Log the error and alert the system administrator. |
