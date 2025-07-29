STORE_DATABASE = {
    "store_id": "5422-Carrollton-Supercenter",
    "store_name": "Carrollton Supercenter",
    "products": {
        "milk": {"id": "p1", "name": "Milk (1 Gallon)", "aisle": 3, "price": 3.50, "stock": 42, "section": "B2"},
        "almond milk": {"id": "p1a", "name": "Almond Milk", "aisle": 3, "price": 4.50, "stock": 25, "section": "B2"},
        "oat milk": {"id": "p1b", "name": "Oat Milk (Half Gallon)", "aisle": 3, "price": 4.00, "stock": 15, "section": "B3"}, # Added Oat Milk
        "eggs": {"id": "p3", "name": "Large Eggs (12 pack)", "aisle": 3, "price": 4.00, "stock": 8, "section": "C1"},
        "bread": {"id": "p2", "name": "White Bread", "aisle": 7, "price": 2.50, "stock": 30, "section": "A1"},
        "pasta": {"id": "p5", "name": "Spaghetti Pasta", "aisle": 8, "price": 1.50, "stock": 50, "section": "A3"},
        "pasta sauce": {"id": "p8", "name": "Marinara Sauce", "aisle": 8, "price": 3.00, "stock": 40, "section": "B2"},
        "ground beef": {"id": "p6", "name": "Ground Beef (1 lb)", "aisle": 15, "price": 8.00, "stock": 25, "section": "D1"},
        "chicken": {"id": "p9", "name": "Chicken Breast", "aisle": 15, "price": 6.50, "stock": 35, "section": "A1"},
        "cereal": {"id": "p15", "name": "Honey Nut Cereal", "aisle": 9, "price": 4.50, "stock": 40, "section": "B1"},
        "bananas": {"id": "p11", "name": "Bananas", "aisle": 1, "price": 1.25, "stock": 80, "section": "A1"},
        "apples": {"id": "p12", "name": "Red Apples", "aisle": 1, "price": 2.00, "stock": 60, "section": "A2"},
        "toilet paper": {"id": "p13", "name": "Toilet Paper (12 rolls)", "aisle": 13, "price": 12.00, "stock": 20, "section": "C3"},
        "shampoo": {"id": "p14", "name": "Shampoo (Volumizing)", "aisle": 12, "price": 5.50, "stock": 25, "section": "A1"},
    },
    "aisle_layout": {
        "1": "Fresh Produce", "2": "Fresh Produce", "3": "Dairy & Refrigerated",
        "4": "Frozen Foods", "5": "Frozen Foods", "6": "Bakery", "7": "Bakery & Bread",
        "8": "Pantry & Dry Goods", "9": "Breakfast & Cereal", "10": "Snacks & Candy",
        "11": "Beverages", "12": "Health & Beauty", "13": "Household Items",
        "14": "Electronics", "15": "Meat & Seafood", "16": "Deli"
    },
    "meal_suggestions": [
        {"trigger_items": ["pasta", "ground beef", "pasta sauce"], "suggestion": "Spaghetti Bolognese"},
        {"trigger_items": ["chicken", "bread"], "suggestion": "Chicken Sandwiches"},
        {"trigger_items": ["eggs", "bread"], "suggestion": "French Toast or Egg Sandwiches"}
    ]
}
