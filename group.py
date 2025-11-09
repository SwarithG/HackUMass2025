import os
from dotenv import load_dotenv
from autogen import GroupChat, GroupChatManager, AssistantAgent, UserProxyAgent
# No need to import google.generativeai or genai directly anymore
# Autogen's internal client will handle it via llm_config

load_dotenv()

# The API key is now passed directly in the llm_config, no need for global genai.configure
api_key = os.getenv("GEMINI_API_KEY")

# Define the shared Gemini LLM configuration
# This config will be used by all agents that need an LLM, including the GroupChatManager
gemini_llm_config = {
    "config_list": [
        {
            "model": "gemini-2.5-flash",
            "api_key": api_key,
            "api_type": "google",
            # 'base_url' can also be added if needed, e.g., for specific Vertex AI endpoints
        }
    ],
    "temperature": 0.7 # This temperature applies to all calls using this llm_config
}

# Now, your agents will inherit from AssistantAgent directly and use the shared llm_config
# Their role will be defined by the 'system_message'
# We no longer need the custom GeminiAssistant class or call_gemini function.

# Create the agents
user = UserProxyAgent(
    name="User",
    code_execution_config={"use_docker": False},
    # Set llm_config to False for UserProxyAgent if it only forwards messages and doesn't generate LLM replies itself.
    # If you want it to also leverage an LLM, pass gemini_llm_config here too.
    llm_config=False
)

planner = AssistantAgent(
    name="PlannerAgent",
    llm_config=gemini_llm_config, # Pass the shared Gemini config
    system_message="Create structured travel itineraries day-by-day given location and duration."
)

researcher = AssistantAgent(
    name="ResearchAgent",
    llm_config=gemini_llm_config, # Pass the shared Gemini config
    system_message="Suggest restaurants, cultural spots, local experiences, and hidden gems for the given destination."
)

coordinator = AssistantAgent(
    name="CoordinatorAgent",
    llm_config=gemini_llm_config, # Pass the shared Gemini config
    system_message="Combine inputs from PlannerAgent and ResearchAgent into one clear, executable travel plan."
)

forecaster = AssistantAgent(
    name="WeatherForecaster",
    llm_config=gemini_llm_config, # Pass the shared Gemini config
    system_message="Give inputs on the weather over the span of the trip at the location specified."
)

groupchat = GroupChat(
    agents=[user, planner, researcher, coordinator, forecaster],
    messages=[],
    max_round=6,
)

manager = GroupChatManager(
    groupchat=groupchat,
    llm_config=gemini_llm_config # GroupChatManager also uses the shared config
)

user.initiate_chat(
    manager,
    message="Plan a 5-day food and culture trip to Kyoto in April."
)