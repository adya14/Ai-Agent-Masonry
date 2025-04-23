# Web Research Agent with Streamlit UI

## Project Description

This project implements a Web Research Agent that uses real-world tools to answer user queries. It leverages:

* **Web Search:** DuckDuckGo Search (`duckduckgo-search`) to find relevant web pages.
* **Web Scraping:** `requests` and `BeautifulSoup4` to extract text content from websites.
* **AI Analysis & Synthesis:** Google's Gemini API (`google-generativeai`) to understand user queries, plan research steps, and synthesize gathered information into a coherent report.
* **User Interface:** Streamlit (`streamlit`) to provide a simple web-based chat interface for interacting with the agent.

The agent analyzes the user's query, searches the web, scrapes relevant pages, and then uses the Gemini LLM to generate a comprehensive answer based on the collected data.

## Features

* Analyzes user query intent using Gemini.
* Performs real-time web searches.
* Scrapes text content from relevant web pages (basic implementation).
* Uses Gemini to synthesize information from multiple sources into a final report.
* Simple and interactive Streamlit web interface.
* Secure API key handling using `.env` file.

## Prerequisites

* **Python:** Version 3.7 or higher.
* **Google Gemini API Key:** You need an API key from Google AI Studio.
    * Get one here: [https://aistudio.google.com/](https://aistudio.google.com/)
    * Note: API usage may incur costs depending on your usage tier.

## Setup Instructions

1.  **Get the Code:**
    * Ensure you have the following files in the same project directory:
        * `app.py` (Streamlit front-end)
        * `research_agent.py` (Backend agent logic with real tools)
        * `requirements.txt` (List of dependencies - provided below)

2.  **Create a Virtual Environment (Recommended):**
    * Open your terminal or command prompt in the project directory.
    * Run:
        ```bash
        # For Linux/macOS
        python3 -m venv venv
        source venv/bin/activate

        # For Windows
        python -m venv venv
        .\venv\Scripts\activate
        ```
    * You should see `(venv)` at the beginning of your terminal prompt.

3.  **Install Dependencies:**
    * Make sure you have the `requirements.txt` file in your project directory.
    * Run:
        ```bash
        pip install -r requirements.txt
        ```

4.  **Set Up Gemini API Key:**
    * Create a file named `.env` in the *same project directory*.
    * Add the following line to the `.env` file, replacing `"YOUR_API_KEY"` with your actual Gemini API key:
        ```
        GEMINI_API_KEY="YOUR_API_KEY"
        ```
    * **Important:** Do not share this file or commit it to version control (like Git). Add `.env` to your `.gitignore` file if using Git.

## Running the Application

1.  **Navigate to Directory:**
    * Open your terminal or command prompt.
    * Use the `cd` command to navigate into the project directory where `app.py` is located.

2.  **Activate Virtual Environment (if not already active):**
    ```bash
    # Linux/macOS: source venv/bin/activate
    # Windows: .\venv\Scripts\activate
    ```

3.  **Run Streamlit:**
    * Execute the command:
        ```bash
        streamlit run app.py
        ```

4.  **Access the UI:**
    * Streamlit will start a local web server and usually open the application automatically in your browser.
    * If not, the terminal will display a local URL (e.g., `http://localhost:8501`). Copy and paste this URL into your web browser.
    * You can now enter queries into the web interface and interact with the agent. The agent's internal processing logs (tool calls, LLM steps) will appear in the terminal where you ran the `streamlit` command.

## File Structure

* `app.py`: Contains the Streamlit code for the user interface.
* `research_agent.py`: Contains the core logic for the `WebResearchAgent` class, including functions for interacting with web search, scraping, and the Gemini LLM.
* `requirements.txt`: Lists all the necessary Python packages.
* `.env`: Stores your secret Gemini API key (you need to create this).
* `README.md`: This file - instructions and information about the project.
* `venv/` (Optional): Directory created for the virtual environment.

## Important Notes

* **API Costs:** Using the Google Gemini API can incur costs. Monitor your usage via the Google Cloud Console or AI Studio dashboard associated with your API key.
* **Web Scraping Ethics:**
    * This agent includes a basic web scraper. Be mindful of website terms of service and `robots.txt` files (which this basic scraper does *not* automatically check).
    * Avoid sending too many requests too quickly to any single website. Use responsibly and ethically.
    * Web scraping can be unreliable as website structures change frequently.
* **Error Handling:** The agent includes basic error handling, but real-world web interactions can fail in many ways (network issues, blocked requests, API errors, etc.).
* **Security:** Keep your `.env` file and API key secure. Do not expose it publicly.
