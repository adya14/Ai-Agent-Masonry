# research_agent.py (Version with REAL Web Search, Scraping, and LLM)

import os
import random
import time
import json
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS # Changed from simulate_web_search
import google.generativeai as genai # Changed from call_llm placeholder
from dotenv import load_dotenv

# --- Load API Key from .env file ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("--------------------------------------------------")
    print("ERROR: GEMINI_API_KEY not found.")
    print("Please create a .env file in the same directory.")
    print("Add the line: GEMINI_API_KEY='YOUR_API_KEY'")
    print("Get your key from https://aistudio.google.com/")
    print("--------------------------------------------------")
    # You might want to raise an exception or exit here in a real app
    # For now, we'll let it proceed but Gemini calls will fail.
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("Gemini API Key configured successfully.")
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")


# --- Tool 1: Real Web Search Tool ---
def real_web_search(query: str, num_results: int = 7) -> list:
    """
    Performs a real web search using DuckDuckGo Search.

    Args:
        query: The search query string.
        num_results: The desired maximum number of results.

    Returns:
        A list of dictionaries, each with 'title', 'href' (link), and 'body' (snippet).
        Returns empty list on error.
    """
    print(f"\n[Real Tool] Searching web for: '{query}' (max {num_results} results)")
    try:
        with DDGS() as ddgs:
            # region='wt-wt' for worldwide results, can be adjusted (e.g., 'in-en' for India)
            # safesearch='off' can be 'moderate' or 'strict'
            results = list(ddgs.text(query, region='wt-wt', safesearch='moderate', max_results=num_results))
        print(f"[Real Tool] Found {len(results)} results.")
        # Adapt keys to match expected format ('link', 'snippet')
        formatted_results = [
            {"title": r.get("title", "No Title"),
             "link": r.get("href", ""),
             "snippet": r.get("body", "")}
            for r in results if r.get("href") # Ensure there's a link
        ]
        return formatted_results
    except Exception as e:
        print(f"[Error] Web search failed: {e}")
        return []

# --- Tool 2: Real Web Scraper Tool ---
def real_web_scraper(url: str, timeout: int = 10) -> dict | None:
    """
    Scrapes text content from a given URL using requests and BeautifulSoup.
    Focuses on extracting paragraph text.

    Args:
        url: The URL to scrape.
        timeout: Request timeout in seconds.

    Returns:
        A dictionary with 'url' and 'extracted_text', or None if scraping fails.
    """
    print(f"[Real Tool] Attempting to scrape content from: {url}")
    # IMPORTANT: Respect robots.txt! A production system needs a robots.txt parser.
    # This basic scraper does NOT check robots.txt. Use responsibly.
    headers = { # Set a user-agent to mimic a browser
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        # Check content type - only parse HTML
        if 'text/html' not in response.headers.get('Content-Type', ''):
            print(f"[Scraper Info] Skipping non-HTML content at {url} (Content-Type: {response.headers.get('Content-Type')})")
            return None

        soup = BeautifulSoup(response.text, 'lxml') # Use lxml parser

        # Basic text extraction: find all paragraph tags and join their text
        paragraphs = soup.find_all('p')
        extracted_text = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

        if not extracted_text:
             # Fallback: try getting all text if no paragraphs found
             print(f"[Scraper Info] No <p> tags found at {url}. Trying body text.")
             body = soup.find('body')
             if body:
                 extracted_text = body.get_text(separator='\n', strip=True)
             else:
                 print(f"[Scraper Warning] Could not find body tag at {url}.")
                 return None # No useful content extracted

        if not extracted_text:
            print(f"[Scraper Warning] No text content extracted from {url}")
            return None

        print(f"[Real Tool] Successfully scraped ~{len(extracted_text)} characters from {url}.")
        # Return only text for simplicity, structured data extraction is complex
        return {
            "url": url,
            "extracted_text": extracted_text,
            "structured_data": None # Keep the key, but no real structured data extraction here
        }

    except requests.exceptions.RequestException as e:
        print(f"[Scraper Error] Failed to fetch {url}: {e}")
        return None
    except Exception as e:
        print(f"[Scraper Error] Failed to parse {url}: {e}")
        return None

# --- Tool 3: News Aggregator (Using Web Search for News) ---
# We can simulate this by refining the web search query for news
def search_for_news(topic: str, num_results: int = 5) -> list:
    """
    Uses the real web search tool, tailoring the query for recent news.

    Args:
        topic: The news topic.
        num_results: Max number of news results (search results).

    Returns:
        A list of search result dictionaries (title, link, snippet) relevant to news.
    """
    # Enhance query for news (could also use specific news search endpoints if available)
    news_query = f"latest news {topic} updates"
    print(f"\n[Real Tool] Searching for news about: '{topic}' using query: '{news_query}'")
    # Use the real_web_search function
    news_results = real_web_search(news_query, num_results=num_results)
    # Adapt results slightly if needed, here we just return search results
    # A more advanced version could try scraping these links for summaries
    # Or use the LLM to summarize the snippets
    return news_results # Returns format: [{'title': ..., 'link': ..., 'snippet': ...}]


# --- LLM Interaction: Real Gemini Call ---
# Ensure GEMINI_API_KEY is configured
generation_config = { # Configure model parameters
  "temperature": 0.7, # Controls randomness (0=deterministic, 1=more creative)
  "top_p": 1.0,
  "top_k": 32,
  "max_output_tokens": 4096, # Adjust as needed
}
safety_settings = [ # Configure safety settings
  {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Choose a Gemini model - 'gemini-1.5-flash' is fast and capable
# Use 'gemini-pro' or 'gemini-1.5-pro' for potentially higher quality but slower/more expensive calls.
llm_model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)

def call_real_llm(prompt: str, model_name: str = "gemini-1.5-flash") -> str:
    """
    Calls the configured Google Gemini model.

    Args:
        prompt: The input prompt for the LLM.
        model_name: Identifier (mainly for logging, actual model set above).

    Returns:
        The text response from the LLM, or an error message.
    """
    print(f"\n--- Calling Real LLM ({model_name}) ---")
    # print(f"Prompt (truncated):\n{prompt[:600].strip()}...") # Log truncated prompt
    if not GEMINI_API_KEY:
        return "Error: Gemini API Key not configured. Cannot call LLM."
    if not llm_model:
         return "Error: Gemini model not initialized."

    try:
        start_time = time.time()
        # Use generate_content for potentially richer responses (including safety feedback)
        response = llm_model.generate_content(prompt)
        end_time = time.time()
        print(f"LLM call took {end_time - start_time:.2f} seconds.")

        # Handle potential blocks or empty responses
        if not response.parts:
             if response.prompt_feedback.block_reason:
                 block_reason = response.prompt_feedback.block_reason
                 print(f"[LLM Safety Block] Reason: {block_reason}")
                 return f"Error: The response was blocked by safety filters (Reason: {block_reason}). Please revise your query or the content gathered."
             else:
                 print("[LLM Warning] Received empty response from LLM.")
                 return "Error: Received an empty response from the language model."

        result_text = response.text
        # print(f"LLM Response (truncated):\n{result_text[:500].strip()}...") # Log truncated response
        print("--- LLM Call Complete ---")
        return result_text

    except Exception as e:
        print(f"[LLM Error] Failed to call Gemini API: {e}")
        # Provide specific feedback if possible (e.g., authentication error, quota exceeded)
        error_message = f"Error interacting with the language model: {e}"
        if "API key not valid" in str(e):
            error_message += "\nPlease check your GEMINI_API_KEY."
        return error_message


# --- The Web Research Agent Class (Using REAL Tools) ---

class WebResearchAgent:
    """
    An agent that performs web research using REAL tools (DDGS, Requests/BS4, Gemini).
    """
    def __init__(self, llm_function=call_real_llm):
        """
        Initializes the agent with real tools and the Gemini LLM interface.
        """
        self.search_tool = real_web_search
        self.scraper_tool = real_web_scraper
        self.news_search_tool = search_for_news # Using adapted search for news
        self.llm = llm_function
        print("Web Research Agent initialized with REAL tools.")

    def _analyze_query(self, user_query: str) -> dict:
        """
        Uses the REAL LLM to analyze the user query and devise a plan.
        """
        print(f"\n--- Step 1: Analyzing Query (using LLM) ---")
        # Improved prompt for real LLM analysis
        prompt = f"""Analyze the following user query to understand the core intent, identify the type of information needed (e.g., factual summary, comparison, recent news, specific data points), and suggest a brief research plan.

User Query: "{user_query}"

Instructions for your analysis:
1.  **Intent:** Briefly describe the user's goal (e.g., "Seeking factual definition", "Looking for latest updates", "Wants comparison").
2.  **Query Type:** Categorize (e.g., Factual, Explanatory, News-focused, Comparative, Opinion-seeking).
3.  **Key Topics/Entities:** List the main subjects or named entities (e.g., "Python requests library", "remote work benefits", "AI regulation India 2025").
4.  **Search Strategy:**
    * Suggest 1-2 optimized search queries for a web search engine (like DuckDuckGo).
    * If the query asks for recent news or updates, suggest 1 specific news-focused query.
    * Mention how many search results should ideally be checked/scraped (e.g., "Check top 3-5 relevant results").

Provide your analysis as a structured response, clearly labeling each section (Intent, Query Type, Key Topics, Search Strategy).
"""
        analysis_text = self.llm(prompt, model_name="gemini-query-analyzer")

        # --- Basic parsing of REAL LLM response ---
        # This parsing is simplistic and relies on the LLM following instructions.
        # More robust parsing (e.g., asking LLM for JSON output) is recommended for production.
        analysis = {}
        current_section = None
        search_queries = []
        news_queries = []
        scrape_count_suggestion = "top 3-5 relevant results" # Default

        for line in analysis_text.split('\n'):
            line = line.strip()
            if not line: continue

            if line.startswith("**Intent:**"): current_section = 'intent'
            elif line.startswith("**Query Type:**"): current_section = 'query_type'
            elif line.startswith("**Key Topics/Entities:**"): current_section = 'key_topics'
            elif line.startswith("**Search Strategy:**"): current_section = 'strategy'
            elif line.startswith("*") and ":" in line and current_section == 'strategy':
                if "search queries:" in line.lower(): current_section = 'strategy_search'
                elif "news-focused query:" in line.lower(): current_section = 'strategy_news'
                elif "results checked:" in line.lower(): current_section = 'strategy_scrape'

            value = line.split(":", 1)[1].strip() if ":" in line else line

            if current_section == 'intent': analysis['intent'] = value
            elif current_section == 'query_type': analysis['query_type'] = value
            elif current_section == 'key_topics': analysis['key_topics'] = [t.strip() for t in value.split(',')]
            elif current_section == 'strategy_search': search_queries.append(value.strip('"'))
            elif current_section == 'strategy_news': news_queries.append(value.strip('"'))
            elif current_section == 'strategy_scrape': scrape_count_suggestion = value

        analysis['suggested_search_terms'] = search_queries if search_queries else [user_query] # Fallback
        analysis['suggested_news_topics'] = news_queries # Can be empty
        analysis['strategy_scrape_suggestion'] = scrape_count_suggestion

        # Basic defaults if parsing fails significantly
        analysis.setdefault('query_type', 'Exploratory')
        analysis.setdefault('key_topics', [kw for kw in user_query.lower().split() if len(kw) > 3])
        analysis.setdefault('suggested_search_terms', [user_query])
        analysis.setdefault('suggested_news_topics', [])
        analysis.setdefault('strategy_scrape_suggestion', 'top 3-5 relevant results')


        print(f"Query Analysis Result: {json.dumps(analysis, indent=2)}")
        return analysis

    def _execute_research_plan(self, user_query: str, analysis: dict) -> dict:
        """
        Executes the research plan using real tools based on the query analysis.
        """
        print(f"\n--- Step 2: Executing Research Plan (Real Tools) ---")
        research_data = {"scraped_content": [], "news_articles": []} # News articles now just search results

        # Determine max pages to scrape based on LLM suggestion (simple parsing)
        max_scrape = 3 # Default
        suggestion = analysis.get('strategy_scrape_suggestion', 'top 3-5').lower()
        if 'top 5' in suggestion or '3-5' in suggestion: max_scrape = 5
        if 'top 1-2' in suggestion or 'top 2' in suggestion: max_scrape = 2
        if 'top 1' in suggestion: max_scrape = 1
        print(f"Analysis suggests checking up to {max_scrape} relevant pages.")

        # Perform Web Search using suggested terms or default
        search_terms = analysis.get('suggested_search_terms', [user_query])
        all_search_results = []
        print(f"Using search query: '{search_terms[0]}'") # Use first suggested query
        search_results = self.search_tool(query=search_terms[0], num_results=max_scrape + 2) # Fetch a few extra
        all_search_results.extend(search_results)

        # Perform News Search (if applicable)
        news_queries = analysis.get('suggested_news_topics', [])
        if news_queries:
            print(f"Checking news using query: '{news_queries[0]}'")
            news_results = self.news_search_tool(topic=news_queries[0], num_results=3) # Limit news results
            research_data["news_articles"] = news_results # Store news *search results*
            # Optionally add these to the main list to consider for scraping
            all_search_results.extend(news_results)


        # Perform Web Scraping on unique, relevant links
        scraped_count = 0
        urls_processed = set()
        unique_results = []
        for res in all_search_results:
            if res['link'] not in urls_processed:
                unique_results.append(res)
                urls_processed.add(res['link'])

        print(f"Attempting to scrape up to {max_scrape} relevant pages from {len(unique_results)} unique results...")

        if unique_results:
            # --- Relevance Check using LLM (Optional but Recommended) ---
            # This adds an extra LLM call but improves quality significantly
            # For simplicity here, we'll stick to keyword check, but an LLM is better.
            links_to_scrape = []
            # Basic relevance check: check if key topics are in title or snippet
            query_keywords = set(analysis.get('key_topics', []))
            for result in unique_results:
                 title_words = set(result['title'].lower().split())
                 snippet_words = set(result['snippet'].lower().split())
                 # Simple check - requires at least one keyword match
                 is_relevant = any(kw.lower() in title_words or kw.lower() in snippet_words for kw in query_keywords)
                 if is_relevant and result['link']:
                     links_to_scrape.append(result)
                 else:
                    print(f"Skipping seemingly non-relevant: {result['title']} ({result['link']})")

            print(f"Found {len(links_to_scrape)} potentially relevant links.")

            for result in links_to_scrape:
                if scraped_count >= max_scrape:
                    print("Reached max scrape limit.")
                    break

                # Add small delay between scrapes to be polite to servers
                time.sleep(random.uniform(0.5, 1.5))

                scraped_data = self.scraper_tool(result['link'])
                if scraped_data:
                    research_data["scraped_content"].append(scraped_data)
                    scraped_count += 1
                # scraper_tool prints errors internally

        print(f"--> Execution Complete: Gathered {len(research_data['scraped_content'])} scraped pages.")
        print(f"--> Found {len(research_data['news_articles'])} news search results (not scraped).")
        return research_data

    def _synthesize_information(self, original_query: str, research_data: dict) -> str:
        """
        Uses the REAL LLM to synthesize the gathered information into a report.
        """
        print(f"\n--- Step 3: Synthesizing Information (using LLM) ---")

        # Prepare context for the LLM, limiting the length of scraped text
        context = f"Original Query: {original_query}\n\n"
        context += "--- Context from Scraped Web Content ---\n"
        scraped_content_available = False
        if research_data["scraped_content"]:
            for i, content in enumerate(research_data["scraped_content"]):
                scraped_content_available = True
                context += f"Source {i+1} (URL: {content['url']}):\n"
                # Limit text length per source significantly to avoid huge prompts
                text_limit = 3000 # Characters per source
                context += content["extracted_text"][:text_limit] + ("..." if len(content["extracted_text"]) > text_limit else "") + "\n"
                context += "---\n"
        else:
            context += "[No web content was successfully scraped or deemed relevant enough to process.]\n"

        context += "\n--- Context from Recent News Search Results (Snippets Only) ---\n"
        news_snippets_available = False
        if research_data["news_articles"]: # These are now search results, not scraped pages
            for i, article_result in enumerate(research_data["news_articles"]):
                news_snippets_available = True
                context += f"News Result {i+1} (Title: {article_result['title']}):\n"
                context += f"Snippet: {article_result['snippet']}\n"
                context += f"Link: {article_result['link']}\n" # Include link for reference
                context += "---\n"
        else:
            context += "[No relevant news search results were found or news check was not requested.]\n"

        # Check if there's any meaningful context to synthesize
        if not scraped_content_available and not news_snippets_available:
             print("[Warning] No scraped content or news snippets available to synthesize.")
             return "I couldn't find and process enough relevant information from the web to answer your query thoroughly. The search might have yielded irrelevant results, or the relevant pages could not be scraped successfully."


        # Refined prompt for synthesis using real data
        prompt = f"""You are a Web Research Agent assistant. Your task is to synthesize the provided context (from web scraping and news search snippets) to answer the user's original query thoroughly and accurately.

Original User Query: "{original_query}"

Provided Context:
{context}

Instructions for Synthesis:
1.  **Answer the Query:** Directly address the user's original query based *only* on the information within the provided context.
2.  **Combine Information:** Integrate insights from different scraped sources and news snippets.
3.  **Identify Key Findings:** Extract and highlight the most important points, facts, or conclusions relevant to the query.
4.  **Structure:** Present the information in a clear, well-organized report format. Use paragraphs, bullet points, or numbered lists where appropriate.
5.  **Acknowledge Limitations:** If the context is insufficient to fully answer the query, state that clearly. If information seems contradictory across sources, mention it briefly. Do not invent information not present in the context.
6.  **Conciseness:** Be informative but avoid unnecessary jargon or overly long sentences. Focus on the essence of the findings.
7.  **Source Attribution (Implicit):** You don't need to cite URLs explicitly in the final report, but ensure your synthesis genuinely reflects the provided source material.

Generate the research report now:
"""
        report = self.llm(prompt, model_name="gemini-synthesis")
        return report

    # research method remains the same as before
    def research(self, user_query: str) -> str:
        """
        Performs the end-to-end research process for a given query using REAL tools.

        Args:
            user_query: The user's research question.

        Returns:
            A string containing the synthesized research report.
        """
        print(f"\n{'='*15} Starting REAL Research for Query: '{user_query}' {'='*15}")

        # 1. Analyze Query (Uses Real LLM)
        analysis = self._analyze_query(user_query)

        # 2. Execute Plan (Real Search, Scrape, News Search)
        research_data = self._execute_research_plan(user_query, analysis)

        # 3. Synthesize Results (Uses Real LLM)
        final_report = self._synthesize_information(user_query, research_data)

        print(f"\n{'='*15} REAL Research Complete for Query: '{user_query}' {'='*15}")
        return final_report

# --- Testing Block (Optional - can be run directly) ---
if __name__ == "__main__":
    print("\n--- Testing Real Web Research Agent ---")
    print("NOTE: This requires a configured GEMINI_API_KEY in a .env file.")

    # Create the agent instance with real tools
    real_agent = WebResearchAgent()

    # Test Query (Requires internet connection and valid API key)
    test_query = "What were the key announcements from Google I/O 2024?" # Adjust year if needed

    # Check if API key seems configured before running a potentially costly test
    if GEMINI_API_KEY:
        print(f"\n--- Running Test Query: '{test_query}' ---")
        test_report = real_agent.research(test_query)
        print("\n--- Test Report ---")
        print(test_report)
        print("-------------------")
    else:
        print("\nSkipping test query execution because GEMINI_API_KEY is not configured.")

    print("\n--- Test Complete ---")