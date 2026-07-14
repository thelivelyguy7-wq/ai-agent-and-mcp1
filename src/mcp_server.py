import os
import sys
import argparse
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP

SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/gmail.compose'
]

# Create the FastMCP server instance
mcp = FastMCP("Workspace Server")

def get_credentials():
    """Handles OAuth 2.0 authentication and token management."""
    # Find the client secret file dynamically based on the uploaded file in the current directory
    client_secret_file = None
    for f in os.listdir("."):
        if f.startswith("client_secret_") and f.endswith(".json"):
            client_secret_file = f
            break
            
    token_file = 'token.json'
    creds = None
    
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not client_secret_file:
                raise FileNotFoundError("Could not find client_secret_*.json file in the root directory. Please download it from Google Cloud Console.")
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            # This opens a browser window for authentication
            creds = flow.run_local_server(port=0)
            
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
            
    return creds

@mcp.tool()
def create_document(title: str, content: str) -> str:
    """
    Create a new Google Document and insert text content into it.
    
    Args:
        title: The title of the new Google Doc.
        content: The text content to insert into the document.
    """
    creds = get_credentials()
    docs_service = build('docs', 'v1', credentials=creds)
    
    # 1. Create empty doc
    document = docs_service.documents().create(body={'title': title}).execute()
    document_id = document.get('documentId')

    # 2. Insert content at the beginning
    requests = [
        {
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        }
    ]
    docs_service.documents().batchUpdate(
        documentId=document_id, body={'requests': requests}).execute()

    return f"https://docs.google.com/document/d/{document_id}/edit"

@mcp.tool()
def create_draft(to: str, subject: str, body: str) -> str:
    """
    Create a new Gmail draft.
    
    Args:
        to: The recipient email address.
        subject: The subject of the email.
        body: The plain text body of the email.
    """
    creds = get_credentials()
    gmail_service = build('gmail', 'v1', credentials=creds)

    message = EmailMessage()
    message.set_content(body)
    message['To'] = to
    message['Subject'] = subject

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'message': {'raw': encoded_message}}

    draft = gmail_service.users().drafts().create(userId='me', body=create_message).execute()
    draft_id = draft['id']
    
    return f"Draft created successfully. ID: {draft_id}"

if __name__ == "__main__":
    # If run with --auth, just do the authentication flow and exit.
    if "--auth" in sys.argv:
        print("Starting OAuth flow...")
        get_credentials()
        print("Authentication successful! token.json has been created.")
    else:
        # Otherwise run the MCP server over stdio
        mcp.run()
