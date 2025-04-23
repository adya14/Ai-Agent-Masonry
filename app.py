import streamlit as st
import time # To potentially add delays or feedback
import sys
import os

# --- Ensure the backend script directory is in the Python path ---
# This helps if running streamlit from a different location, though best practice
# is to run it from the directory containing both app.py and research_agent.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- Import the Backend Agent ---
# This assumes research_agent.py is in the same directory
try:
    from research_agent import WebResearchAgent
except ImportError:
    st.error(
        "Error: Could not find the backend agent file 'research_agent.py'. "
        "Please ensure 'research_agent.py' is in the same directory as 'app.py'."
    )
    st.stop() # Stop execution if the backend can't be imported


# --- Page Configuration ---
st.set_page_config(
    page_title="Web Research Agent",
    page_icon="💡", # Changed icon
    layout="centered", # Use "wide" for more horizontal space if needed
    initial_sidebar_state="collapsed", # Keep sidebar collapsed initially
)

# --- Styling (Optional - Minor tweaks using Markdown) ---
st.markdown("""
<style>
    /* Center align the title */
    .stApp > header {
        background-color: transparent;
    }
    h1 {
        text-align: center;
        color: #333; /* Darker title color */
    }
    /* Style the caption */
    .stApp [data-testid="stCaptionContainer"] > p {
        text-align: center;
        color: #555; /* Slightly darker caption */
    }
    /* Style the submit button */
    .stButton>button {
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        background-color: #007bff; /* Blue button */
        color: white;
        font-weight: bold;
        transition: background-color 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #0056b3; /* Darker blue on hover */
    }
    .stTextInput input {
         border-radius: 0.5rem; /* Rounded input box */
    }
     /* Style the report area */
    [data-testid="stMarkdownContainer"] {
        background-color: #f9f9f9; /* Light grey background for report */
        border-radius: 0.5rem;
        padding: 1rem 1.5rem;
        border: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)


# --- App Title and Description ---
st.title("💡 Web Research Agent")
st.caption("Enter your research query. The agent will simulate searching the web, extracting information, and compiling a report for you.")


# --- Initialize Agent (Option 1: Initialize once per session) ---
# Use Streamlit's session state to keep the agent instance if needed,
# but for this simulation, creating a new one per query is simpler and ensures fresh state.
# if 'research_agent' not in st.session_state:
#     st.session_state.research_agent = WebResearchAgent()
# agent = st.session_state.research_agent

# --- Input Form ---
# Using a form prevents Streamlit from rerunning the script on every interaction inside the form
with st.form("research_query_form"):
    user_query = st.text_area( # Use text_area for potentially longer queries
        "Enter your query here:",
        placeholder="e.g., Compare the benefits of solar vs. wind energy.",
        height=100,
    )
    submit_button = st.form_submit_button("Start Research")


# --- Process Query and Display Results ---
if submit_button and user_query:
    st.markdown("---") # Separator
    st.info(f"Processing query: \"{user_query[:100]}...\"" if len(user_query) > 100 else f"Processing query: \"{user_query}\"")

    # Show spinner during processing
    with st.spinner("🤖 Agent at work... Analyzing query, searching, scraping (simulated), and synthesizing report... Please wait."):
        try:
            # --- Initialize Agent (Option 2: Initialize fresh per query) ---
            # Best for this simulation as the agent has no complex state to maintain
            agent = WebResearchAgent()

            # Run the research - the agent's internal prints go to console
            start_time = time.time()
            final_report = agent.research(user_query)
            end_time = time.time()

            # Display the final report
            st.success(f"Research completed in {end_time - start_time:.2f} seconds!")
            st.subheader("📄 Research Report")
            st.markdown(final_report) # Display the report content

        except ImportError as ie:
             # This handles the case where the file exists but has issues
             st.error(f"Failed to use the backend agent from 'research_agent.py'. Error: {ie}")
        except Exception as e:
            st.error("An unexpected error occurred during the research process.")
            st.exception(e) # Shows the full error traceback in the UI for debugging

elif submit_button and not user_query:
    st.warning("⚠️ Please enter a query before starting the research.")

# --- Footer ---
st.markdown("---")
st.markdown("Simulated agent using Python & Streamlit. Agent's internal logs (simulated tool/LLM calls) appear in the console where Streamlit is running.")