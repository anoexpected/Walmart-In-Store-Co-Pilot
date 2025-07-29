# FILE: mcp_client/agent.py
# FIXED: Switched back to ReAct agent since ChatOllama doesn't support tool calling

from langchain_ollama import ChatOllama
from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
import json
import asyncio
import re
from typing import Dict, Any, List, Optional

from mcp_client.config import OLLAMA_MODEL, OLLAMA_BASE_URL
from mcp_client.client import MCPConnector

class WallabyAgent:
    def __init__(self, mcp_connector: MCPConnector):
        self.mcp_connector = mcp_connector
        self.llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0)
        self.agent_executor = None
        self.last_processed_items: List[Dict[str, Any]] = []
        self._setup_agent()

    def _setup_agent(self):
        """Set up the agent with MCP tools using the ReAct method."""
        try:
            tools = [
                Tool(
                    name="find_item",
                    description="Find a single, specific item in the store to get its location, price, and stock. Use for simple, one-item queries.",
                    func=self._sync_find_item,
                    coroutine=self._async_find_item
                ),
                Tool(
                    name="process_shopping_list",
                    description="Processes a list of multiple items to find their locations and total cost. Input must be a comma-separated string of item names.",
                    func=self._sync_process_shopping_list,
                    coroutine=self._async_process_shopping_list
                ),
                Tool(
                    name="get_meal_suggestions",
                    description="Suggests meals or identifies missing ingredients for a desired meal. Use this to find ingredients for a meal.",
                    func=self._sync_get_meal_suggestions,
                    coroutine=self._async_get_meal_suggestions
                ),
                 Tool(
                    name="get_item_stock",
                    description="Check the current stock quantity for a specific item.",
                    func=self._sync_get_item_stock,
                    coroutine=self._async_get_item_stock
                ),
                Tool(
                    name="get_aisle_info",
                    description="Get a list of all products in a specific aisle number.",
                    func=self._sync_get_aisle_info,
                    coroutine=self._async_get_aisle_info
                ),
                # *** NEW TOOL DEFINITION ***
                Tool(
                    name="browse_products",
                    description="Browse or search for products based on a category (e.g., 'Fresh Produce') or a maximum price. Use this for complex questions about finding items under a certain budget or in a general category.",
                    func=self._sync_browse_products,
                    coroutine=self._async_browse_products
                ),
                Tool(
                    name="no_op",
                    description="Use this when no tool is needed.",
                    func=lambda x: "No tool used.",
                    coroutine=lambda x: asyncio.sleep(0, result="No tool used.")
                )

            ]
            
            # *** FIX ***: The prompt has been significantly rewritten to be clearer and more direct,
            # guiding the agent's strategy and preventing it from misinterpreting instructions.
            prompt = PromptTemplate.from_template("""
You are Wallaby, a helpful Walmart shopping assistant. Your goal is to assist the user efficiently and accurately.

You have access to the following tools:
{tools}

**Your Decision Guide:**
- For simple factual questions, store hours, store policies, your identity, or general shopping advice (like budgeting, tips to avoid overspending, or planning a shopping trip), answer directly without using any tool by calling the 'no_op' tool ONCE and then provide your final answer.
- For "where is X?" questions, use `find_item`.
- For shopping lists, always use `process_shopping_list`.
- For meal suggestions or cooking advice, use `get_meal_suggestions` first.
- For budget or category-specific browsing (e.g., "what's under $5?" or "what's in the bakery?"), use `browse_products`.
- Never ask the user for information you can retrieve with a tool.
- Do not use a tool if you don't have all the required inputs.
- If a tool response indicates "no items found" or provides no useful information, STOP using tools and use 'no_op' to give a direct answer.

**Output Format:**
You MUST strictly follow this sequence in your response:

Thought: Your reasoning and plan to solve the user's question.
Action: The name of the tool to use, which must be one of [{tool_names}]. If no tool is needed, write 'no_op'.
Action Input: The input for the chosen tool. If no tool is used, write 'None'.
Observation: The result from the tool, or write 'No tool used.' if 'no_op' is called.

**IMPORTANT**: After using 'no_op' or getting a tool result, you MUST immediately provide your final answer:

Thought: I now have all the information needed to answer the user's question.
Final Answer: Your final, conversational answer to the original question.

**Critical Rules:**
- Always follow the exact output format.
- Never skip 'Action Input:' even when it is 'None.'
- After using any tool (including no_op), immediately move to "Final Answer"
- Do not repeat tool calls unnecessarily
- Keep responses helpful and conversational

Begin!

Question: {input}
Thought:{agent_scratchpad}
""")



            agent = create_react_agent(self.llm, tools, prompt)
            
            self.agent_executor = AgentExecutor(
                agent=agent, 
                tools=tools, 
                verbose=True,
                max_iterations=5, 
                handle_parsing_errors=True
            )
            
            print("✅ Agent successfully set up with ReAct method.")
            
        except Exception as e:
            print(f"❌ Error setting up agent: {e}")
            raise e

    # --- Sync/Async Tool Wrappers ---
    def _sync_find_item(self, item_name: str) -> str:
        return asyncio.run(self._async_find_item(item_name))
    
    def _sync_process_shopping_list(self, items_str: str) -> str:
        return asyncio.run(self._async_process_shopping_list(items_str))
    
    # *** FIX ***: Made the input handling more robust. It now extracts the integer
    # from strings like "3 (Dairy & Refrigerated)", preventing validation errors.
    def _sync_get_aisle_info(self, aisle_input: str) -> str:
        try:
            # Use regex to find the first sequence of digits
            match = re.match(r'\d+', str(aisle_input).strip())
            if not match:
                return "Error: A valid aisle number could not be found in the input."
            aisle_number = int(match.group(0))
            return asyncio.run(self._async_get_aisle_info(aisle_number))
        except (ValueError, TypeError):
            return "Error: Aisle number must be an integer."
    
    def _sync_get_store_layout(self, *args, **kwargs) -> str:
        return asyncio.run(self._async_get_store_layout())

    def _sync_get_meal_suggestions(self, items_str: str) -> str:
        return asyncio.run(self._async_get_meal_suggestions(items_str))

    def _sync_report_out_of_stock(self, item_name: str) -> str:
        return asyncio.run(self._async_report_out_of_stock(item_name))

    def _sync_get_item_stock(self, item_name: str) -> str:
        return asyncio.run(self._async_get_item_stock(item_name))
        
    def _sync_browse_products(self, query: str) -> str:
        # A simple parser for the query string, e.g., "category: Bakery, max_price: 5.0"
        kwargs = {}
        parts = [p.strip() for p in query.split(',')]
        for part in parts:
            try:
                key, value = part.split(':', 1)
                key = key.strip()
                value = value.strip()
                if key == 'max_price':
                    kwargs['max_price'] = float(value)
                elif key == 'category':
                    kwargs['category'] = str(value)
            except ValueError:
                continue # Ignore malformed parts
        return asyncio.run(self._async_browse_products(**kwargs))


    async def _async_find_item(self, item_name: str) -> str:
        result = await self.mcp_connector.find_item(item_name.strip())
        if result.get("found"): self.last_processed_items = [result.get("item", {})]
        return json.dumps(result)
    
    async def _async_process_shopping_list(self, items_str: str) -> str:
        items = [item.strip() for item in items_str.split(',')]
        result = await self.mcp_connector.process_shopping_list(items)
        if result.get("optimized_path"): self.last_processed_items = result.get("optimized_path", [])
        return json.dumps(result)
    
    async def _async_get_aisle_info(self, aisle_number: int) -> str:
        return json.dumps(await self.mcp_connector.get_aisle_info(aisle_number))
    
    async def _async_get_store_layout(self, *args, **kwargs) -> str:
        return json.dumps(await self.mcp_connector.get_store_layout())

    async def _async_get_meal_suggestions(self, items_str: str) -> str:
        items = [item.strip() for item in items_str.split(',')]
        return json.dumps(await self.mcp_connector.get_meal_suggestions(items))

    async def _async_report_out_of_stock(self, item_name: str) -> str:
        return json.dumps(await self.mcp_connector.report_out_of_stock(item_name.strip()))

    async def _async_get_item_stock(self, item_name: str) -> str:
        return json.dumps(await self.mcp_connector.get_item_stock(item_name.strip()))
        
    async def _async_browse_products(self, category: Optional[str] = None, max_price: Optional[float] = None) -> str:
        return json.dumps(await self.mcp_connector.browse_products(category, max_price))

    # --- Main Processing Logic ---
    async def process_message(self, user_message: str) -> Dict[str, Any]:
        if not self.agent_executor:
            return {"message": "Agent not initialized."}
        
        try:
            if user_message.strip().lower() in ["hi", "hello", "hey"]:
                return {"message": "Hello! I'm Wallaby, your shopping assistant. How can I help you today?"}

            self.last_processed_items.clear()
            result = await self.agent_executor.ainvoke({"input": user_message})
            response_text = result.get("output", "I'm sorry, I couldn't process your request.")
            
            structured_data = self._extract_structured_data_from_last_run()

            return {"message": response_text, **structured_data}
            
        except Exception as e:
            error_message = f"Error during agent execution: {e}"
            print(f"❌ {error_message}")
            import traceback
            traceback.print_exc()
            self.last_processed_items.clear()
            return {"message": "I'm sorry, I ran into a technical problem while trying to answer. Could you please try rephrasing your request?"}

    def _extract_structured_data_from_last_run(self) -> Dict[str, Any]:
        """Extracts structured data from the last tool call for the UI."""
        if not self.last_processed_items: return {}
        
        data = {
            "aisles": sorted(list(set(item['aisle'] for item in self.last_processed_items if 'aisle' in item))),
            "total_cost": round(sum(item['price'] for item in self.last_processed_items if 'price' in item), 2),
            "items_found": len(self.last_processed_items),
            "individual_item_costs": {item['name']: item['price'] for item in self.last_processed_items if 'name' in item and 'price' in item},
        }
        return data