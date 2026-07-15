# Autonomous AI Product Feedback Pipeline 🚀

An end-to-end, autonomous data pipeline that ingests raw user reviews (App Store/Play Store), sanitizes them for privacy, and uses Large Language Models (LLMs) to generate executive-level "Weekly Pulse" reports.

This project uses the **Model Context Protocol (MCP)** to natively authenticate and interface with Google Workspace, automatically publishing the formatted report to a Google Doc and drafting a notification email to stakeholders.

## 🌟 Key Features

*   **Privacy-First Sanitization:** Automatically strips out Personally Identifiable Information (PII), excessive emojis, and malformed strings before any data hits the LLM.
*   **Intelligent Thematic Clustering:** Uses Groq (LLaMA/Mixtral) to analyze hundreds of reviews, grouping them into Top Themes.
*   **Actionable Insights:** Extracts real, verbatim user quotes (minimum 8 words) and translates complaints into concrete roadmap action items for Product & Growth teams.
*   **Native Google Workspace Integration:** Leverages MCP to securely connect to Google Drive and Gmail. The system dynamically generates a perfectly formatted, scannable Google Doc (complete with specific bolding and underline rules) without relying on unstable Markdown-to-Docs conversions.
*   **Cloud-Native & Serverless:** Fully containerized and deployed on Railway. Runs autonomously via a cron job using a `railway.json` configuration to prevent infinite boot-loops.

## 🛠 Tech Stack

*   **Language:** Python 3.11
*   **LLM Provider:** Groq API (High-speed inference)
*   **Integrations:** Model Context Protocol (FastMCP), Google Docs API, Gmail API
*   **Data Handling:** Pandas, Pydantic (Data validation)
*   **Infrastructure:** Railway (Nixpacks)

## 🏗 Architecture Overview

1.  **Ingestion & Sanitization (`src/ingestion.py`):** Loads `.csv` data, filters out non-English reviews, enforces length rules, and applies PII sanitization.
2.  **LLM Processing (`src/main.py` & `src/prompts.py`):** Batches the cleaned data to respect token limits and prompts the LLM to output a strictly formatted 250-word report.
3.  **MCP Server (`src/mcp_server.py`):** Acts as the bridge to Google Workspace. It parses the LLM output, generates native Google Docs `batchUpdate` requests (for custom borders and specific bolded headers), and creates the Gmail draft.

## 🚀 How It Works (For Stakeholders)

1.  The script wakes up on a schedule.
2.  It pulls the latest App/Play store reviews.
3.  It generates a restricted Google Doc containing:
    *   **Top Themes**
    *   **User Quotes**
    *   **Three Action Ideas**
4.  It leaves a Draft in the Product Manager's Gmail inbox linking directly to the new, private report.
