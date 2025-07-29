# FILE: mcp_client/client.py
# Enhanced MCP Client with better timeout handling and error recovery

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from mcp import ClientSession
from mcp.client.sse import sse_client
from .config import MCP_SERVER_HTTP_URL

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WalmartMCPClient:
    """Enhanced MCP Client with better timeout and error handling."""
    
    def __init__(self, server_url: str = MCP_SERVER_HTTP_URL):
        self.server_url = server_url
        self.session: Optional[ClientSession] = None
        self.connected = False
        self._sse_context = None
        self._connection_lock = asyncio.Lock()
        
    async def connect(self, timeout: float = 10.0) -> bool:
        """Connect to the MCP server using SSE transport with timeout."""
        async with self._connection_lock:
            try:
                await self._cleanup_on_error() 
                
                logger.info(f"🔌 Connecting to MCP server at {self.server_url}")
                
                # Use timeout for connection
                async with asyncio.timeout(timeout):
                    self._sse_context = sse_client(self.server_url)
                    read_stream, write_stream = await self._sse_context.__aenter__()
                    
                    self.session = ClientSession(read_stream, write_stream)
                    await self.session.__aenter__()
                
                self.connected = True
                logger.info("✅ Successfully connected to MCP server")
                
                await self._initialize_session()
                return True
                        
            except asyncio.TimeoutError:
                logger.error(f"❌ Connection timeout after {timeout}s")
                self.connected = False
                await self._cleanup_on_error()
                return False
            except Exception as e:
                logger.error(f"❌ Failed to connect to MCP server: {e}")
                self.connected = False
                await self._cleanup_on_error()
                return False
    
    async def _cleanup_on_error(self):
        """Clean up resources on connection error or before new connection."""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
                self.session = None
            
            if self._sse_context:
                await self._sse_context.__aexit__(None, None, None)
                self._sse_context = None
        except Exception as e:
            logger.warning(f"⚠️ Error during cleanup: {e}")
    
    async def _initialize_session(self):
        """Initialize the MCP session and get server capabilities."""
        if not self.session:
            logger.warning("Session not available for initialization.")
            return
            
        try:
            # Initialize with timeout
            async with asyncio.timeout(5.0):
                result = await self.session.initialize()
                logger.info(f"📋 Session initialized: {result}")
                
                tools_result = await self.session.list_tools()
                available_tools = [tool.name for tool in tools_result.tools]
                logger.info(f"🛠️ Available tools: {available_tools}")
                
                # Check for tool name issues
                if 'find_itemm' in available_tools:
                    logger.warning("⚠️ Found 'find_itemm' - there might be a typo in the MCP server")
                
                try:
                    resources_result = await self.session.list_resources()
                    logger.info(f"📚 Available resources: {[resource.name for resource in resources_result.resources]}")
                except Exception as e:
                    logger.warning(f"⚠️ No resources available or error listing resources: {e}")
                    
        except asyncio.TimeoutError:
            logger.error("❌ Session initialization timed out")
            self.connected = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize session: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            self.connected = False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any], timeout: float = 15.0, retry: bool = True) -> Dict[str, Any]:
        """Call a tool on the MCP server with configurable timeout and retry."""
        # Handle potential tool name typos
        if tool_name == "find_item" and not self.connected:
            # Try to reconnect first
            if not await self.connect():
                return {"error": "Failed to connect to server"}
        
        if not self.session or not self.connected:
            logger.error("❌ Not connected to MCP server. Attempting to reconnect...")
            if not await self.connect():
                return {"error": "Failed to connect to server"}
            
        try:
            logger.info(f"🔧 Calling tool '{tool_name}' with args: {arguments}")
            
            # Use timeout for tool calls
            async with asyncio.timeout(timeout):
                result = await self.session.call_tool(tool_name, arguments)
            
            if result.isError:
                logger.error(f"❌ Tool call failed: {result.content}")
                if isinstance(result.content, list) and result.content and hasattr(result.content[0], 'text'):
                    return {"error": result.content[0].text}
                elif hasattr(result.content, 'text'):
                    return {"error": result.content.text}
                else:
                    return {"error": str(result.content)}
            
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    try:
                        parsed_result = json.loads(content.text)
                        logger.info(f"✅ Tool call successful")
                        return parsed_result
                    except json.JSONDecodeError:
                        logger.info(f"✅ Tool call successful (plain text)")
                        return {"result": content.text}
                else:
                    logger.info(f"✅ Tool call successful (raw content)")
                    return {"result": str(content)}
            
            logger.info(f"✅ Tool call successful (empty result)")
            return {"result": "Tool executed successfully"}
            
        except asyncio.TimeoutError:
            logger.error(f"❌ Tool call '{tool_name}' timed out after {timeout}s")
            return {"error": f"Tool call timed out after {timeout} seconds"}
        except Exception as e:
            error_msg = str(e)
            if "ClosedResourceError" in error_msg and retry:
                logger.warning(f"Connection lost while calling tool '{tool_name}'. Attempting to reconnect and retry...")
                self.connected = False
                if await self.connect():
                    logger.info("Reconnection successful. Retrying tool call.")
                    return await self.call_tool(tool_name, arguments, timeout=timeout, retry=False)
                else:
                    logger.error("Failed to reconnect. Cannot retry tool call.")
                    return {"error": f"Connection lost and failed to reconnect: {error_msg}"}
            else:
                logger.error(f"❌ Error calling tool '{tool_name}': {e}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a simple health check of the MCP connection."""
        if not self.connected:
            return {"healthy": False, "reason": "Not connected"}
        
        try:
            # Try a simple tool call with short timeout
            result = await self.call_tool("get_store_layout", {}, timeout=5.0)
            if "error" in result:
                return {"healthy": False, "reason": f"Tool call failed: {result['error']}"}
            return {"healthy": True, "last_check": "get_store_layout successful"}
        except Exception as e:
            return {"healthy": False, "reason": f"Health check failed: {str(e)}"}
    
    # --- Tool Methods with Better Error Handling ---
    async def find_item(self, item_name: str) -> Dict[str, Any]:
        """Find an item with fallback for tool name typos."""
        # First try the correct tool name
        result = await self.call_tool("find_item", {"item_name": item_name}, timeout=10.0)
        
        # If it fails due to tool not found, try the typo version
        if "error" in result and "not found" in result["error"].lower():
            logger.warning("⚠️ find_item not found, trying find_itemm")
            result = await self.call_tool("find_itemm", {"item_name": item_name}, timeout=10.0)
        
        return result
    
    async def process_shopping_list(self, items: List[str]) -> Dict[str, Any]:
        return await self.call_tool("process_shopping_list", {"items": items}, timeout=20.0)
    
    async def get_aisle_info(self, aisle_number: int) -> Dict[str, Any]:
        return await self.call_tool("get_aisle_info", {"aisle_number": aisle_number}, timeout=5.0)
    
    async def get_store_layout(self) -> Dict[str, Any]:
        return await self.call_tool("get_store_layout", {}, timeout=5.0)

    async def get_meal_suggestions(self, items: List[str]) -> Dict[str, Any]:
        return await self.call_tool("get_meal_suggestions", {"items": items}, timeout=15.0)

    async def report_out_of_stock(self, item_name: str) -> Dict[str, Any]:
        return await self.call_tool("report_out_of_stock", {"item_name": item_name}, timeout=5.0)

    async def get_item_stock(self, item_name: str) -> Dict[str, Any]:
        return await self.call_tool("get_item_stock", {"item_name": item_name}, timeout=5.0)
    
    async def browse_products(self, category: Optional[str] = None, max_price: Optional[float] = None) -> Dict[str, Any]:
        """Call the browse_products tool, handling optional arguments."""
        args = {}
        if category:
            args["category"] = category
        if max_price is not None:
            args["max_price"] = max_price
        return await self.call_tool("browse_products", args, timeout=10.0)

    # --- Resource Reading Methods ---
    async def get_product_catalog(self) -> Dict[str, Any]:
        """Get the complete product catalog resource."""
        if not self.session or not self.connected:
            return {"error": "Not connected to server"}
        try:
            async with asyncio.timeout(10.0):
                resource_name = "http://localhost/product_catalog"
                logger.info(f"📚 Reading resource: {resource_name}")
                result = await self.session.read_resource(resource_name)
                if result.contents and len(result.contents) > 0 and hasattr(result.contents[0], 'text'):
                    return json.loads(result.contents[0].text)
                return {"error": "Could not retrieve product catalog."}
        except asyncio.TimeoutError:
            return {"error": "Timeout reading product catalog"}
        except Exception as e:
            logger.error(f"❌ Error reading product_catalog resource: {e}")
            return {"error": str(e)}

    async def get_store_map_layout(self) -> Dict[str, Any]:
        """Get the store map layout resource."""
        if not self.session or not self.connected:
            return {"error": "Not connected to server"}
        try:
            async with asyncio.timeout(10.0):
                resource_name = "http://localhost/store_map_layout"
                logger.info(f"📚 Reading resource: {resource_name}")
                result = await self.session.read_resource(resource_name)
                if result.contents and len(result.contents) > 0 and hasattr(result.contents[0], 'text'):
                    return json.loads(result.contents[0].text)
                return {"error": "Could not retrieve store map layout."}
        except asyncio.TimeoutError:
            return {"error": "Timeout reading store map layout"}
        except Exception as e:
            logger.error(f"❌ Error reading store_map_layout resource: {e}")
            return {"error": str(e)}

    async def disconnect(self):
        """Disconnect from the MCP server."""
        async with self._connection_lock:
            try:
                if self.session:
                    await self.session.__aexit__(None, None, None)
                    self.session = None
                if self._sse_context:
                    await self._sse_context.__aexit__(None, None, None)
                    self._sse_context = None
                logger.info("🔌 Disconnected from MCP server")
            except Exception as e:
                logger.error(f"❌ Error disconnecting: {e}")
            finally:
                self.session = None
                self.connected = False
                self._sse_context = None


class MCPConnector:
    """Enhanced singleton connector with better error handling."""
    
    _instance: Optional['MCPConnector'] = None
    _client: Optional[WalmartMCPClient] = None
    _connection_lock = asyncio.Lock()
    
    def __init__(self):
        if MCPConnector._instance is not None:
            raise Exception("MCPConnector is a singleton class")
        MCPConnector._instance = self
    
    @classmethod
    async def get_instance(cls) -> 'MCPConnector':
        """Get or create the singleton instance with connection retry."""
        async with cls._connection_lock:
            if cls._instance is None:
                cls._instance = MCPConnector()
            
            if cls._client is None or not cls._client.connected:
                cls._client = WalmartMCPClient()
                
                # Try to connect with retries
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        success = await cls._client.connect(timeout=10.0)
                        if success:
                            break
                    except Exception as e:
                        logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
                if not cls._client.connected:
                    raise Exception("Failed to connect to MCP server after retries")
            
            return cls._instance
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the MCP connection."""
        if not self._client:
            return {"healthy": False, "reason": "Client not initialized"}
        
        return await self._client.health_check()
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool through the MCP client with automatic reconnection."""
        if not self._client:
            try:
                await MCPConnector.get_instance()
            except Exception as e:
                logger.error(f"Failed to get connected MCP client: {e}")
                return {"error": "MCP client not initialized or failed to connect"}
        
        return await self._client.call_tool(tool_name, params)
    
    # --- Exposed Client Methods ---
    async def find_item(self, item_name: str) -> Dict[str, Any]:
        if not self._client: 
            return {"error": "MCP client not initialized"}
        return await self._client.find_item(item_name)
    
    async def process_shopping_list(self, items: List[str]) -> Dict[str, Any]:
        if not self._client: 
            return {"error": "MCP client not initialized"}
        return await self._client.process_shopping_list(items)
    
    async def get_aisle_info(self, aisle_number: int) -> Dict[str, Any]:
        if not self._client: 
            return {"error": "MCP client not initialized"}
        return await self._client.get_aisle_info(aisle_number)
    
    async def get_store_layout(self) -> Dict[str, Any]:
        if not self._client: 
            return {"error": "MCP client not initialized"}
        return await self._client.get_store_layout()

    async def get_meal_suggestions(self, items: List[str]) -> Dict[str, Any]:
        if not self._client: 
            return {"error": "MCP client not initialized"}
        return await self._client.get_meal_suggestions(items)

    async def report_out_of_stock(self, item_name: str) -> Dict[str, Any]:
        if not self._client: 
            return {"error": "MCP client not initialized"}
        return await self._client.report_out_of_stock(item_name)

    async def get_item_stock(self, item_name: str) -> Dict[str, Any]:
        if not self._client: 
            return {"error": "MCP client not initialized"}
        return await self._client.get_item_stock(item_name)
    
    async def browse_products(self, category: Optional[str] = None, max_price: Optional[float] = None) -> Dict[str, Any]:
        if not self._client: 
            return {"error": "MCP client not initialized"}
        return await self._client.browse_products(category=category, max_price=max_price)
    
    async def get_product_catalog(self) -> Dict[str, Any]:
        if not self._client: 
            return {"error": "MCP client not initialized"}
        return await self._client.get_product_catalog()

    async def get_store_map_layout(self) -> Dict[str, Any]:
        if not self._client: 
            return {"error": "MCP client not initialized"}
        return await self._client.get_store_map_layout()

    async def cleanup(self):
        """Clean up the MCP connection."""
        if self._client:
            await self._client.disconnect()
            self._client = None