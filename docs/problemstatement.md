# Problem Statement: AI-Powered Mobile Review Pulse

## 1. Executive Summary
Product, support, and leadership teams currently struggle to extract actionable insights from raw mobile store (App Store and Google Play) reviews efficiently. The goal of this project is to develop an automated system that turns raw mobile-store feedback into a weekly "pulse" document. This system will aggregate, theme, and summarize user feedback, and then deliver these insights directly to stakeholders via Google Docs and Gmail, using the Model Context Protocol (MCP) to avoid complex REST API wiring.

## 2. Objectives
* **Automation:** Eliminate the manual effort required to read, categorize, and summarize weekly user reviews.
* **Actionability:** Surface the top themes, real user verbatim quotes, and concrete next steps.
* **Seamless Integration:** Deliver the final artifacts into familiar surfaces (Google Docs and Gmail) using MCP.
* **Privacy:** Ensure strict adherence to data privacy by sanitizing all Personally Identifiable Information (PII) from the reports.

## 3. Scope of Work

### 3.1 In-Scope
* Ingesting exported public reviews (last 8–12 weeks) containing fields like rating, title, text, and date.
* Processing and clustering reviews into a maximum of 5 predefined themes (e.g., onboarding, KYC, payments).
* Generating a single-page weekly note (≤250 words) that highlights the top 3 themes, 3 user quotes, and 3 actionable ideas.
* Publishing the note to Google Docs using an MCP server.
* Drafting an email linking to or containing the note in Gmail using an MCP server.

### 3.2 Out-of-Scope
* Web scraping of review stores or bypassing store logins (must use public review exports only).
* Direct integration with Google APIs via custom OAuth/REST clients (must use MCP).
* Handling and storage of PII (usernames, emails, device IDs).

## 4. Target Audience & Value Proposition

| Audience | Needs Addressed |
| :--- | :--- |
| **Product / Growth** | Prioritize fixes and product improvements based on real user signals. |
| **Support** | Align support messaging and documentation with actual user terminology. |
| **Leadership** | Obtain a high-level, scannable one-page health check without drowning in raw data. |

## 5. Deliverables
1. **Data Ingestion Script/Module:** To parse the exported review files.
2. **AI Theming & Summarization Engine:** To cluster themes and extract quotes/action items.
3. **Weekly Pulse Artifact (Google Doc):** The resulting one-page scannable summary.
4. **Notification Artifact (Gmail):** A drafted email containing the pulse note.

## 6. Key Constraints
* **Integration Method:** Must utilize Model Context Protocol (MCP) servers for Google Docs and Gmail.
* **Theming Limit:** Maximum of 5 themes considered; only the top 3 reported.
* **Data Quality Filters:** Reviews must be in English, contain at least 8 words, and have no emojis.
* **Content Constraints:** Strict adherence to word counts (≤250 words) and use of exact verbatim quotes (no hallucinations).
* **Privacy & Security:** Zero PII allowed in any generated artifact.
