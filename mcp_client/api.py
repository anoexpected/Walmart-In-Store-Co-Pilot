# FILE: mcp_client/api.py
# Updated API with proper agent integration

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

from .client import MCPConnector
from .agent import WallabyAgent

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    message: str
    aisles: list | None = None
    total_cost: float | None = None
    items_found: int | None = None
    individual_item_costs: Dict[str, float] | None = None # New field for individual prices
    suggestions: List[str] | None = None # New field for meal suggestions

# --- Global Agent Instance ---
wallaby_agent: WallabyAgent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages startup and shutdown events."""
    global wallaby_agent
    # Startup
    print("🚀 API Server starting up...")
    
    try:
        # Initialize MCP connector
        mcp_connector = await MCPConnector.get_instance()
        print("✅ MCP Connector initialized")
        
        # Initialize agent with MCP connector
        wallaby_agent = WallabyAgent(mcp_connector)
        print("✅ Wallaby Agent initialized")
        
        print("✅ API Server is ready.")
        
    except Exception as e:
        print(f"❌ Failed to initialize server: {e}")
        raise e
    
    yield
    
    # Shutdown
    print("🛑 API Server shutting down...")
    try:
        connector = await MCPConnector.get_instance()
        await connector.cleanup()
        print("✅ Cleanup complete.")
    except Exception as e:
        print(f"⚠️ Error during cleanup: {e}")

# --- FastAPI App Setup ---
app = FastAPI(title="Walmart Co-Pilot Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---
@app.get("/")
def health_check():
    return {"status": "Wallaby API is online"}

@app.get("/debug/tools")
async def debug_tools():
    """Debug endpoint to test MCP tools directly."""
    if not wallaby_agent or not wallaby_agent.mcp_connector:
        raise HTTPException(status_code=503, detail="Agent is not initialized yet.")
    
    try:
        # Test each tool
        results = {}
        
        # Test find_item
        find_result = await wallaby_agent.mcp_connector.call_tool("find_item", {"item_name": "milk"})
        results["find_item"] = find_result
        
        # Test get_store_layout
        layout_result = await wallaby_agent.mcp_connector.call_tool("get_store_layout", {})
        results["get_store_layout"] = layout_result

        # Test new tool: get_meal_suggestions
        meal_suggest_result = await wallaby_agent.mcp_connector.get_meal_suggestions(["pasta", "ground beef"])
        results["get_meal_suggestions"] = meal_suggest_result

        # Test new tool: get_item_stock
        item_stock_result = await wallaby_agent.mcp_connector.get_item_stock("eggs")
        results["get_item_stock"] = item_stock_result

        # Test new tool: report_out_of_stock
        report_oos_result = await wallaby_agent.mcp_connector.report_out_of_stock("almond milk")
        results["report_out_of_stock"] = report_oos_result

        # Test new resource: get_product_catalog
        product_catalog_result = await wallaby_agent.mcp_connector.get_product_catalog()
        results["product_catalog_sample"] = list(product_catalog_result.items())[:1] # Get first item as sample

        # Test new resource: get_store_map_layout
        store_map_layout_result = await wallaby_agent.mcp_connector.get_store_map_layout()
        results["store_map_layout_sample"] = store_map_layout_result # Return full layout as it's small


        return results
        
    except Exception as e:
        print(f"❌ Error in debug endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Debug error: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    if not wallaby_agent:
        raise HTTPException(status_code=503, detail="Agent is not initialized yet.")
    
    try:
        print(f"📨 Received chat request: {request.message}")
        response_data = await wallaby_agent.process_message(request.message)
        print(f"📤 Sending response: {response_data}")
        return ChatResponse(**response_data)
        
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")
