import os
import sys
import asyncio
import argparse
import logging
from dotenv import load_dotenv

from src.ingestion import load_reviews
from src.ai_engine import AIEngine
from src.mcp_client import get_workspace_client, ToolExecutionError

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def main(csv_path: str):
    # Load environment variables (API Keys, MCP Server Paths)
    load_dotenv()
    
    logger.info("--- Phase 1: Data Ingestion & Sanitization ---")
    try:
        reviews = load_reviews(csv_path)
        logger.info(f"Loaded {len(reviews)} valid reviews for processing.")
    except Exception as e:
        logger.error(f"Failed to load reviews: {e}")
        sys.exit(1)
        
    logger.info("--- Phase 2: MCP Health Checks ---")
    workspace_client = get_workspace_client()
    
    logger.info("Checking Workspace MCP Server...")
    workspace_healthy = await workspace_client.check_health()
    
    if not workspace_healthy:
        logger.error("Workspace MCP Server is unreachable. The system cannot create docs or send notifications. Aborting.")
        sys.exit(1)
    
    logger.info("--- Phase 3: AI Processing ---")
    engine = AIEngine()
    try:
        pulse_document = engine.generate_pulse(reviews)
        logger.info("Successfully generated pulse document.")
    except Exception as e:
        logger.error(f"AI generation failed: {e}")
        sys.exit(1)
        
    logger.info("--- Phase 4: MCP Publishing ---")
    doc_url = None
    
    if workspace_healthy:
        try:
            logger.info("Attempting to publish document via Google Docs MCP...")
            result = await workspace_client.execute_tool(
                "create_document", 
                {"title": "Weekly Mobile Review Pulse", "content": pulse_document}
            )
            
            # The MCP server might return a dict or string based on its schema
            if isinstance(result, dict):
                doc_url = result.get('url', str(result))
            elif hasattr(result, "content") and result.content:
                # Standard MCP call_tool result often has .content[] list
                # Just stringifying it for simplicity in MVP
                doc_url = str(result.content[0].text if hasattr(result.content[0], 'text') else result.content)
            else:
                doc_url = str(result)
                
            logger.info(f"Successfully published to Google Docs: {doc_url}")
            
        except ToolExecutionError as e:
            logger.error(f"Failed to publish to Google Docs: {e}")
            workspace_healthy = False
            
    # Fallback Mechanism: If Docs failed, send full text via email
    try:
        target_email = os.getenv("STAKEHOLDER_EMAIL", "team@example.com")
        
        if workspace_healthy and doc_url:
            logger.info("Drafting notification email with Document Link...")
            email_body = f"Hello Team,\n\nThe weekly mobile review pulse is ready. You can view it here: {doc_url}\n\nBest,\nAI Agent"
            subject = "Weekly Mobile Review Pulse - Published"
        else:
            logger.warning("Docs failed. Falling back to sending the full pulse document within the email draft.")
            email_body = f"Hello Team,\n\nHere is the weekly mobile review pulse:\n\n{pulse_document}\n\nBest,\nAI Agent"
            subject = "Weekly Mobile Review Pulse - Fallback"
            
        await workspace_client.execute_tool(
            "create_draft",
            {
                "to": target_email,
                "subject": subject,
                "body": email_body
            }
        )
        logger.info("Successfully created Gmail draft.")
        
    except ToolExecutionError as e:
        logger.error(f"Failed to create Gmail draft: {e}")
        sys.exit(1)
        
    logger.info("Pipeline execution completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the AI-Powered Mobile Review Pulse pipeline")
    parser.add_argument("csv_path", type=str, help="Path to the exported reviews CSV/JSON file")
    args = parser.parse_args()
    
    asyncio.run(main(args.csv_path))
