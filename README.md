# 🛒 Walmart In-Store Co-Pilot

This is my project submission for the Walmart Global Tech Sparkathon Hackathon – July 2025. The application aims to enhance the in-store shopping experience by providing a helpful AI assistant that can locate items, process shopping lists, suggest meals, and offer real-time information about products within a Walmart Supercenter.

## ✨ Features

- **Intelligent Item Location:** Ask "Where is milk?" and get precise aisle numbers.
- **Shopping List Optimization:** Provide a list of items, and the Co-Pilot will help you find them, potentially optimizing your path.
- **Meal Suggestions:** Get recipe ideas based on items you have or need, with a focus on finding necessary ingredients.
- **Price and Stock Checks:** Quickly check the price and current stock levels of any item.
- **Interactive Store Map:** Visualize item locations on an interactive store map, with highlighted aisles for easy navigation.
- **User-Friendly Chat Interface:** A conversational interface powered by a large language model (LLM) makes interactions intuitive.
- **Backend Connectivity:** Integrates with a Model Context Protocol (MCP) server to access real-time store data.

## 🚀 Demo

Watch a walkthrough of the Walmart In-Store Co-Pilot in action:

## 🚀 Demo

Watch a walkthrough of the Walmart In-Store Co-Pilot in action:

<a href="https://youtu.be/kC1vfyucOKQ" target="_blank">
  <img src="https://img.youtube.com/vi/kC1vfyucOKQ/maxresdefault.jpg" alt="Walmart Co-Pilot Demo" style="width:100%; max-width:800px; display:block; margin:auto;" />
</a>


## 🛠️ Technologies Used

### Frontend
- **HTML5:** Structure of the web application.
- **CSS3 (Tailwind CSS):** Utility-first CSS framework for rapid UI development.
- **JavaScript:** Powers the interactive elements and communication with the backend.

### Backend
- **Python:** Backend programming language.
- **FastAPI:** Web framework for building APIs.
- **fastmcp:** Library for connecting to the MCP server.
- **LangChain:** Agent framework for tool integration and orchestration.
- **Ollama:** Runs LLMs locally (e.g., Llama 3.1) for assistant logic.
- **Pydantic:** Data validation using type hints.
- **Uvicorn:** ASGI server for serving the FastAPI app.

## ⚙️ Setup and Installation

### Prerequisites

Before you begin, ensure you have the following installed:

-   [Python 3.9+](https://www.python.org/downloads/)
-   [Node.js (for npm/yarn, if you use it for frontend build tools, though not strictly required for this project's simple setup)](https://nodejs.org/en/download/)
-   [Git](https://git-scm.com/downloads)
-   [Ollama](https://ollama.com/download): To run the local LLM. After installing Ollama, pull the specified model:
    ```bash
    ollama pull llama3.1 # Or the model specified in mcp_client/config.py
    ```

### Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
    cd Walmart-Co-Pilot
    ```
    (Replace `YOUR_USERNAME` and `YOUR_REPOSITORY_NAME` with your actual GitHub details)

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    -   **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    -   **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install backend dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the FastAPI backend:**
    Navigate to the root directory where `api.py` is located.
    ```bash
    uvicorn api:app --reload --port 8080
    ```
    This will start the API server, typically accessible at `http://127.0.0.1:8080`.

### Frontend Setup

The frontend is a static HTML/CSS/JavaScript application. You simply need to open `index.html` in your web browser. Ensure the backend is running first.

1.  **Open `index.html`:**
    You can directly open the `index.html` file in your preferred web browser (e.g., `file:///path/to/your/project/index.html`).

    Alternatively, for development, you can use a simple Python HTTP server:
    ```bash
    python -m http.server 8000
    ```
    Then, open `http://localhost:8000` in your browser.

## 🤝 Contributing

We welcome contributions to the Walmart In-Store Co-Pilot project! If you have ideas for new features, bug fixes, or improvements, please feel free to:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'feat: Add new feature X'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Open a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file (if you choose to add one) for details.

---

**Remember to replace placeholders like `YOUR_USERNAME`, `YOUR_REPOSITORY_NAME`, and the actual YouTube video ID in both the `README.md` and the `git clone` command.**




