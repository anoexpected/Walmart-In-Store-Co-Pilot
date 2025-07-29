# FILE: server.py
# MCP Server using Anthropic's FastMCP SDK

from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
import json

# Import your store data
from mcp_client.data import STORE_DATABASE

# Create the MCP server instance
mcp = FastMCP("Walmart Store Assistant")

def fuzzy_search_product(item_name: str) -> Dict[str, Any] | None:
    """Search for a product using fuzzy matching."""
    item_lower = item_name.lower().strip()
    
    if item_lower in STORE_DATABASE['products']:
        return STORE_DATABASE['products'][item_lower]

    for key, product in STORE_DATABASE['products'].items():
        product_name_lower = product['name'].lower()
        if item_lower in product_name_lower or product_name_lower in item_lower:
            return product
        
        query_words = set(item_lower.split())
        product_words = set(product_name_lower.split())
        
        if query_words.intersection(product_words):
            return product

    return None

### ENHANCEMENT: This function is now smarter.
def get_shopping_suggestions(items: List[str]) -> Dict[str, Any]:
    """Get meal suggestions based on items in the shopping list, and suggest missing items."""
    results = {"suggestions": [], "missing_items": {}}
    item_names_lower = [item.lower() for item in items]
    
    for suggestion_rule in STORE_DATABASE['meal_suggestions']:
        trigger_items = [t.lower() for t in suggestion_rule['trigger_items']]
        
        present_triggers = [t for t in trigger_items if any(t in user_item for user_item in item_names_lower)]
        
        if not present_triggers:
            continue

        if len(present_triggers) == len(trigger_items):
            results["suggestions"].append(suggestion_rule['suggestion'])
        elif len(present_triggers) > 0:
            missing = [t for t in trigger_items if t not in present_triggers]
            if missing:
                results["missing_items"][suggestion_rule['suggestion']] = missing
    
    return results

### CRITICAL FIX: The tool name typo is corrected here.
@mcp.tool()
def find_item(item_name: str) -> Dict[str, Any]:
    """Find a specific item in the store and return its location and details (price, stock)."""
    product = fuzzy_search_product(item_name)
    
    if not product:
        return { "found": False, "message": f"Sorry, I couldn't find '{item_name}' in our store inventory." }
    
    aisle_name = STORE_DATABASE['aisle_layout'].get(str(product['aisle']), f"Aisle {product['aisle']}")
    stock_status = "Low stock" if product['stock'] < 10 else "In stock"
    if product['stock'] == 0:
        stock_status = "Out of stock"
    
    return {
        "found": True,
        "item": product,
        "location": f"Aisle {product['aisle']} ({aisle_name}), Section {product['section']}",
        "stock_status": stock_status,
        "message": f"Found '{product['name']}' in {aisle_name} (Aisle {product['aisle']}), Section {product['section']}. Price: ${product['price']:.2f}"
    }

@mcp.tool()
def process_shopping_list(items: List[str]) -> Dict[str, Any]:
    """Process a shopping list and return optimized path through the store, estimated total cost, and suggestions."""
    found_items, not_found_items = [], []
    
    for item_name in items:
        # Prevent processing of instructional text from the agent
        if "input should be" in item_name.lower():
            not_found_items.append(item_name)
            continue
            
        product = fuzzy_search_product(item_name)
        if product:
            found_items.append(product)
        else:
            not_found_items.append(item_name)
    
    optimized_path = sorted(found_items, key=lambda x: x['aisle'])
    total_cost = sum(item['price'] for item in found_items)
    unique_aisles = sorted(list(set(item['aisle'] for item in found_items)))
    
    suggestion_results = get_shopping_suggestions([item['name'] for item in found_items])
    
    return {
        "optimized_path": optimized_path,
        "items_found": len(found_items),
        "items_not_found": not_found_items,
        "aisles_to_visit": unique_aisles,
        "total_estimated_cost": round(total_cost, 2),
        "smart_suggestions": suggestion_results.get("suggestions", []),
        "summary": f"Found {len(found_items)} items across {len(unique_aisles)} aisles. Estimated total: ${total_cost:.2f}"
    }

@mcp.tool()
def get_aisle_info(aisle_number: int) -> Dict[str, Any]:
    """Get information about what products are in a specific aisle."""
    if str(aisle_number) not in STORE_DATABASE['aisle_layout']:
        return {"error": f"Aisle {aisle_number} does not exist."}
    
    aisle_products = [p for p in STORE_DATABASE['products'].values() if p['aisle'] == aisle_number]
    aisle_name = STORE_DATABASE['aisle_layout'][str(aisle_number)]
    
    return {
        "aisle_number": aisle_number,
        "aisle_name": aisle_name,
        "products": sorted(aisle_products, key=lambda x: x['name']),
        "total_products": len(aisle_products)
    }

@mcp.tool()
def get_store_layout() -> Dict[str, Any]:
    """Get the complete store layout and general information."""
    return {
        "store_id": STORE_DATABASE['store_id'],
        "store_name": STORE_DATABASE['store_name'],
        "aisle_layout": STORE_DATABASE['aisle_layout']
    }

### *** NEW TOOL & FIX ***
@mcp.tool()
def browse_products(category: Optional[str] = None, max_price: Optional[float] = None) -> Dict[str, Any]:
    """Browse and filter all products by category (e.g., 'Fresh Produce') or a maximum price. Useful for budget or discovery queries."""
    results = []
    category_lower = category.lower() if category else None

    for product in STORE_DATABASE['products'].values():
        # Price filtering
        if max_price is not None and product['price'] > max_price:
            continue
        
        # Category filtering - ENHANCED LOGIC
        if category_lower:
            aisle_name = STORE_DATABASE['aisle_layout'].get(str(product['aisle']), "").lower()
            product_name = product['name'].lower()
            # Check if category is in the aisle OR in the product name
            if category_lower not in aisle_name and category_lower not in product_name:
                continue
        
        results.append(product)

    # Sort results by price, cheapest first
    sorted_results = sorted(results, key=lambda x: x['price'])
    
    return {
        "count": len(sorted_results),
        "products": sorted_results[:20], # Return at most 20 items to avoid overload
        "message": f"Found {len(sorted_results)} items matching the criteria."
    }


### ENHANCEMENT: This tool now returns missing items.
@mcp.tool()
def get_meal_suggestions(items: List[str]) -> Dict[str, Any]:
    """Get meal suggestions based on a list of items. Can also suggest missing ingredients for a meal."""
    suggestion_results = get_shopping_suggestions(items)
    message = "Here are some ideas based on your items."
    if not suggestion_results.get("suggestions") and not suggestion_results.get("missing_items"):
        message = "No specific meal suggestions found for the provided items."

    return {
        "query_items": items,
        "suggestions": suggestion_results.get("suggestions"),
        "missing_for_meal": suggestion_results.get("missing_items"),
        "message": message
    }

@mcp.tool()
def report_out_of_stock(item_name: str) -> Dict[str, Any]:
    """Report an item as being out of stock. This helps the store update its inventory."""
    return { "status": "success", "message": f"Thank you for reporting that '{item_name}' is out of stock." }

@mcp.tool()
def get_item_stock(item_name: str) -> Dict[str, Any]:
    """Get the current stock quantity for a specific item."""
    product = fuzzy_search_product(item_name)
    if not product:
        return {"stock": 0, "stock_status": "Not found", "message": f"Sorry, I couldn't find '{item_name}'." }
    
    stock_status = "In stock"
    if product['stock'] == 0: stock_status = "Out of stock"
    elif product['stock'] < 10: stock_status = "Low stock"

    return { "item_name": product['name'], "stock": product['stock'], "stock_status": stock_status }

# --- Resources ---
@mcp.resource("http://localhost/product_catalog")
def product_catalog() -> Dict[str, Any]:
    """Provides the complete list of products available in the store."""
    return STORE_DATABASE['products']

@mcp.resource("http://localhost/store_map_layout")
def store_map_layout() -> Dict[str, Any]:
    """Provides the complete aisle layout of the store."""
    return STORE_DATABASE['aisle_layout']

if __name__ == "__main__":
    print("🏪 Starting MCP Server with SSE transport...")
    mcp.run(transport="sse", port = "5001")