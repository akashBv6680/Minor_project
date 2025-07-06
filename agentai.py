# streamlit_app.py

import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI  # We'll use OpenAI as an example LLM provider

# --- Configuration and Setup ---

# Load environment variables from .env file for local development.
# Streamlit Cloud uses st.secrets, which os.getenv automatically accesses.
load_dotenv()


# Initialize OpenAI client
# This function is cached to ensure the client is only initialized once,
# even across Streamlit reruns.
@st.cache_resource
def get_openai_client():
    """Initializes and returns the OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        st.error("OpenAI API Key not found. Please set it in your .env file (local) or Streamlit Secrets (cloud).")
        st.stop()  # Stop the app if the key is missing

    try:
        client = OpenAI(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {e}")
        st.stop()


# Get the OpenAI client instance
openai_client = get_openai_client()


# --- Define Agent Tools (Step 4 from your guide: Build a Tool Layer) ---
# These are functions your AI agent can call to perform specific actions.
# In a real agent, you'd have many more complex tools.

def get_current_weather(location: str) -> str:
    """
    Fetches the current weather for a given location.
    This is a placeholder function. In a real application,
    this would call an external weather API (e.g., OpenWeatherMap).
    """
    st.info(f"Agent is calling a weather tool for: {location}...")
    # Simulate an API call
    if location.lower() == "kochi":
        return "The current weather in Kochi is 30°C and sunny. (Simulated)"
    elif location.lower() == "london":
        return "The current weather in London is 18°C and cloudy. (Simulated)"
    else:
        return f"Weather data for {location} is not available. (Simulated)"


# Dictionary of available tools the agent can use.
# Keys are tool names, values are the actual Python functions.
available_tools = {
    "get_current_weather": get_current_weather,
    # Add more tools here (e.g., search_database, send_email, calculate_something)
}


# --- AI Agent Core Logic (Steps 2, 5, 6, 7 from your guide) ---
# This class encapsulates the agent's behavior.
class AIAgent:
    def __init__(self, client: OpenAI, model_name: str = "gpt-3.5-turbo"):
        self.client = client
        self.model_name = model_name
        # Initialize conversation history (Step 5: Maintain Memory or Context)
        # We'll use Streamlit's session_state for persistence across reruns.
        if "messages" not in st.session_state:
            st.session_state.messages = []
            # Add an initial system message to guide the agent's behavior
            st.session_state.messages.append(
                {"role": "system",
                 "content": "You are a helpful AI assistant named Jarvis. You can answer questions and use tools. If asked about weather, try to use the weather tool."}
            )

    def chat(self, user_input: str) -> str:
        """
        Processes user input, uses tools if necessary, and generates a response
        using the LLM. This is where the reasoning strategy is implemented.
        """
        # Add user's message to the conversation history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # --- Step 6: Design the Reasoning Strategy ---
        # This is a simplified reasoning strategy. For a complex agent,
        # you'd use more advanced techniques like function calling, RAG,
        # or multi-step reasoning.

        # 1. Check if a tool needs to be called based on user input (very basic keyword detection)
        if "weather" in user_input.lower() and "in" in user_input.lower():
            try:
                # Simple extraction of location (you'd use NLP for robustness)
                location = user_input.lower().split("in")[-1].strip().split('?')[0].strip()
                if location:
                    # Call the tool
                    tool_output = available_tools["get_current_weather"](location.capitalize())
                    # Add tool output to conversation history (important for LLM context)
                    st.session_state.messages.append(
                        {"role": "tool", "content": tool_output, "name": "get_current_weather"})
                    # Now, ask the LLM to summarize the tool output or continue the conversation
                    prompt_for_llm = f"The user asked about weather in {location}. I used the get_current_weather tool and got this result: '{tool_output}'. Please provide a user-friendly response based on this."
                    st.session_state.messages.append({"role": "user",
                                                      "content": prompt_for_llm})  # Add this as a user message for the LLM to process

            except Exception as e:
                tool_output = f"Error calling weather tool: {e}"
                st.session_state.messages.append(
                    {"role": "tool", "content": tool_output, "name": "get_current_weather_error"})
                st.warning(f"Could not use weather tool: {e}")
                # Fallback to LLM without tool output if tool fails

        # 2. Call the Large Language Model (Step 2: Choose Your Language Model)
        # This is the core interaction with OpenAI's API.
        try:
            # Use the entire conversation history as context for the LLM
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=st.session_state.messages,
                temperature=0.7,  # Adjust creativity
                max_tokens=150  # Limit response length
            )
            agent_response_content = response.choices[0].message.content
        except Exception as e:
            agent_response_content = f"I'm sorry, I encountered an error communicating with the AI model: {e}"
            st.error(f"LLM API Error: {e}")

        # Add agent's response to conversation history
        st.session_state.messages.append({"role": "assistant", "content": agent_response_content})

        return agent_response_content


# --- Streamlit Application Interface ---

st.title("My AI Agent: Jarvis")
st.markdown("Ask me anything! I can also tell you the weather in Kochi or London.")


# Initialize the AI agent instance (cached for efficiency)
@st.cache_resource
def get_agent_instance():
    return AIAgent(client=openai_client)


agent = get_agent_instance()

# Display chat messages from history on app rerun
# Skip the initial system message when displaying to the user
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(message["content"])
    # You might choose to display tool messages differently or not at all
    # elif message["role"] == "tool":
    #     with st.chat_message("tool"):
    #         st.markdown(f"Tool used ({message['name']}): {message['content']}")

# Accept user input
if prompt := st.chat_input("What's on your mind?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent's response and display it
    with st.spinner("Jarvis is thinking..."):
        response = agent.chat(prompt)

    with st.chat_message("assistant"):
        st.markdown(response)
