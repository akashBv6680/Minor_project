# streamlit_app.py
import streamlit as st
import os
from dotenv import load_dotenv

# Import your AI agent logic (assuming you put it in agent_core.py)
# from agent_core import AIAgent, get_weather # Import what's relevant

# --- Load Environment Variables ---
# This loads variables from a .env file locally.
# Streamlit Cloud uses Streamlit Secrets for environment variables.
load_dotenv()


# --- Initialize AI Agent (or just the LLM client) ---
# It's better to initialize expensive objects outside the main function
# to avoid re-running on every interaction.
# Using st.cache_resource for objects that should only be created once.
@st.cache_resource
def get_ai_agent():
    """Initializes and returns the AI agent."""

    # Ensure your API key is loaded.
    # For Streamlit Cloud, it will come from st.secrets
    # For local, it will come from .env
    # Example for OpenAI:
    # openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]
    # if not openai_api_key:
    #     st.error("OpenAI API Key not found. Please set it in .env or Streamlit Secrets.")
    #     return None

    # Placeholder for the actual agent
    # return AIAgent(llm_model_name="gpt-3.5-turbo")

    # Simple placeholder function that mimics an agent
    class SimplePlaceholderAgent:
        def chat(self, user_input):
            if "hello" in user_input.lower():
                return "Hi there! How can I help you today?"
            elif "weather in" in user_input.lower():
                # This would typically call your get_weather tool
                location = user_input.lower().split("weather in")[1].strip().split('?')[0].strip().capitalize()
                return f"Currently, the weather in {location} is sunny and 25°C. (Placeholder response)"
            else:
                return f"I received your message: '{user_input}'. I'm a simple placeholder agent. Please implement my full logic!"

    return SimplePlaceholderAgent()


agent = get_ai_agent()

if agent is None:
    st.stop()  # Stop if agent couldn't be initialized (e.g., missing API key)

st.title("My AI Agent Chatbot")

# --- Initialize Chat History in Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat Messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input ---
if prompt := st.chat_input("Ask your AI Agent..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent's response
    with st.spinner("Agent thinking..."):
        agent_response = agent.chat(prompt)  # Call your AI agent's chat method

    # Add agent's response to chat history
    st.session_state.messages.append({"role": "agent", "content": agent_response})
    with st.chat_message("agent"):
        st.markdown(agent_response)