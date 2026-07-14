import os
import sys
import logging
from typing import Dict, Any, AsyncGenerator
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)

class ToolExecutionError(Exception):
    """Custom exception for MCP tool execution failures."""
    pass

class MCPClientWrapper:
    """
    A wrapper around the MCP ClientSession to securely interface with an MCP server 
    over stdio without needing to handle OAuth natively in this application.
    """
    def __init__(self, command: str, args: list[str]):
        self.server_params = StdioServerParameters(command=command, args=args, env=os.environ.copy())
        
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[ClientSession, None]:
        """Context manager to initialize and yield an active MCP session."""
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    yield session
        except Exception as e:
            logger.error(f"Failed to connect to MCP server ({self.server_params.command} {' '.join(self.server_params.args)}): {e}")
            raise ToolExecutionError(f"Connection failed: {e}")

    async def check_health(self) -> bool:
        """
        Verify the server is reachable and can return its tool list.
        Useful to run before invoking expensive LLM processing.
        """
        try:
            async with self.get_session() as session:
                tools = await session.list_tools()
                logger.info(f"Health check passed. Connected and found {len(tools.tools)} tools.")
                return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a specific tool on the MCP server and return the result.
        """
        async with self.get_session() as session:
            try:
                result = await session.call_tool(tool_name, arguments)
                return result
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                raise ToolExecutionError(f"Tool {tool_name} failed: {e}")

# Factory functions to get configured clients

def get_workspace_client() -> MCPClientWrapper:
    """Returns a configured MCP client for the custom unified Workspace server."""
    server_cmd = os.getenv("WORKSPACE_MCP_COMMAND", sys.executable if sys.executable else "python")
    # By default, point to our custom server script
    script_path = os.path.join(os.path.dirname(__file__), "mcp_server.py")
    args = [script_path]
    
    return MCPClientWrapper(command=server_cmd, args=args)
