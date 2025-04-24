import streamlit as st
import time
import sys
import os

# --- Ensure the backend script directory is in the Python path ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- Import the Backend Agent ---
try:
    from research_agent import WebResearchAgent
except ImportError:
    st.error(
        "**Error:** Could not find the backend agent file 'research_agent.py'. "
        "Please ensure 'research_agent.py' is in the same directory as 'app.py'."
    )
    st.stop() # Stop execution if the backend can't be imported


# --- Page Configuration (More options) ---
st.set_page_config(
    page_title="AI Web Research Assistant",
    page_icon="🤖", # Using a robot emoji
    layout="wide", # Use wide layout for more space
    initial_sidebar_state="collapsed",
)

# --- Enhanced Styling with CSS ---
st.markdown("""
<style>
    /* Import a Google Font (optional, might not always work perfectly in Streamlit) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* General Body Styling */
    body {
        font-family: 'Inter', sans-serif; /* Apply the font */
        background-color: #f0f2f6; /* Light grey background */
    }

    /* Main App Container */
    .stApp {
        /* background: linear-gradient(to bottom right, #e0e7ff, #c7d2fe); */ /* Subtle gradient */
         background-color: #f0f2f6;
    }

    /* Hide Streamlit Header/Footer */
    /* Use cautiously, might hide useful elements */
     header {visibility: hidden;}
     footer {visibility: hidden;}
     /* #MainMenu {visibility: hidden;} */ /* Uncomment to hide hamburger menu */


    /* Title Styling */
    h1 {
        font-family: 'Inter', sans-serif;
        text-align: center;
        color: #1e3a8a; /* Dark blue */
        font-weight: 700;
        padding-top: 2rem; /* Add some space above title */
    }

    /* Caption Styling */
    .stApp [data-testid="stCaptionContainer"] > p {
        text-align: center;
        color: #4b5563; /* Grey text */
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Input Area Styling */
    [data-testid="stForm"] {
        background-color: #ffffff; /* White background for form */
        padding: 2rem 2.5rem;
        border-radius: 1rem; /* More rounded corners */
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); /* Subtle shadow */
        border: 1px solid #e5e7eb; /* Light border */
        margin-bottom: 2rem; /* Space below the form */
    }

    [data-testid="stTextArea"] label {
        font-weight: 600;
        color: #1e3a8a; /* Dark blue label */
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }

    [data-testid="stTextArea"] textarea {
        border: 1px solid #d1d5db;
        border-radius: 0.5rem;
        padding: 0.75rem;
        font-size: 1rem;
        background-color: #f9fafb; /* Slightly off-white background */
        min-height: 120px; /* Ensure decent height */
    }
    [data-testid="stTextArea"] textarea:focus {
        border-color: #3b82f6; /* Blue border on focus */
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.4); /* Focus ring */
    }

    /* Button Styling */
    .stButton>button {
        width: 100%; /* Make button full width */
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 0.5rem;
        background: linear-gradient(to right, #3b82f6, #1d4ed8); /* Blue gradient */
        color: white;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        cursor: pointer; /* Hand cursor on hover */
    }
    .stButton>button:hover {
        background: linear-gradient(to right, #1d4ed8, #3b82f6); /* Reverse gradient on hover */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px); /* Slight lift effect */
    }
    .stButton>button:active {
         transform: translateY(0px); /* Press down effect */
         box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }

    /* Separator Styling */
    hr {
        border-top: 1px solid #d1d5db; /* Lighter separator */
        margin: 2rem 0;
    }

    /* Output Area Styling */
    [data-testid="stExpander"] {
        background-color: #ffffff;
        border-radius: 0.75rem;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        margin-top: 1.5rem;
    }
    [data-testid="stExpander"] > div[role="button"] { /* Expander header */
        font-weight: 600;
        color: #1e3a8a;
        font-size: 1.1rem;
        padding: 0.8rem 1.2rem;
    }
     [data-testid="stExpander"] [data-testid="stMarkdownContainer"] { /* Content inside expander */
        padding: 1rem 1.2rem;
        font-size: 1rem;
        line-height: 1.6;
        color: #374151; /* Dark grey text */
        background-color: #f9fafb; /* Slightly different background for content */
        border-top: 1px solid #e5e7eb; /* Separator line */
    }

    /* Styling for Success/Info/Warning boxes */
    [data-testid="stAlert"] {
        border-radius: 0.5rem;
        padding: 1rem;
        font-size: 1rem;
    }
    [data-testid="stAlert"] > div[role="alert"] { /* Inner container */
       align-items: center; /* Center icon and text vertically */
    }


</style>
""", unsafe_allow_html=True)


# --- App Title and Description ---
# Using columns for better centering and control in wide layout
col1, col2, col3 = st.columns([1, 3, 1]) # Adjust ratios as needed
with col2:
    st.title("🤖 AI Web Research Assistant")
    st.caption("Enter your query below, and the AI agent will research the web to provide a synthesized report.")


# --- Input Form Container ---
with st.container():
    # Use columns again to center the form in wide layout
    form_col1, form_col2, form_col3 = st.columns([1, 2, 1]) # Make middle column wider
    with form_col2:
        with st.form("research_query_form"):
            user_query = st.text_area(
                "🧠 Your Research Query:", # Added icon
                placeholder="e.g., What are the latest advancements in quantum computing?",
                height=150, # Slightly taller
                label_visibility="collapsed" # Hide label, use placeholder
            )
            submit_button = st.form_submit_button("🚀 Start Research")


# --- Process Query and Display Results ---
if submit_button and user_query:
    # Use columns to center the output section
    res_col1, res_col2, res_col3 = st.columns([1, 4, 1]) # Wider middle column for results
    with res_col2:
        st.markdown("---") # Separator
        st.info(f"Processing query: \"{user_query[:100]}...\"" if len(user_query) > 100 else f"Processing query: \"{user_query}\"")

        # Show spinner during processing
        with st.spinner("⏳ Agent is analyzing, searching, and synthesizing... Please hold on!"):
            try:
                # Initialize Agent (fresh per query)
                agent = WebResearchAgent()

                # Run the research
                start_time = time.time()
                final_report = agent.research(user_query)
                end_time = time.time()

                # Display the final report in an expander
                st.success(f"✅ Research completed in {end_time - start_time:.2f} seconds!")

                with st.expander("📄 View Research Report", expanded=True):
                    st.markdown(final_report) # Display the report content

            except ImportError as ie:
                 st.error(f"❌ Failed to use the backend agent from 'research_agent.py'. Error: {ie}")
            except Exception as e:
                st.error("❌ An unexpected error occurred during the research process.")
                st.exception(e) # Shows the full error traceback

elif submit_button and not user_query:
     res_col1, res_col2, res_col3 = st.columns([1, 4, 1])
     with res_col2:
        st.warning("⚠️ Please enter a query before starting the research.")

# --- Footer ---
st.markdown("---")
# Centered footer text
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    AI Research Agent | Powered by Streamlit & Google Gemini
    <br>
    <span style="font-size: 0.8rem;">(Agent's internal logs appear in the console)</span>
</div>
""", unsafe_allow_html=True)

