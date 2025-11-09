import os
from dotenv import load_dotenv
from autogen import GroupChat, GroupChatManager, AssistantAgent, UserProxyAgent
import json # For handling JSON responses
import requests # For making HTTP requests to external APIs (e.g., weather, search)
from tavily import TavilyClient
import urllib.request
import json

load_dotenv()

# The API key for Gemini is now passed directly in the llm_config
gemini_api_key = os.getenv("GEMINI_API_KEY")
tavilyKey = os.getenv("TAVILY_API_KEY")

# --- Define Helper Functions (Tools) ---

# Placeholder for a web search tool.
# In a real scenario, this would call a search API (e.g., Serper, Tavily).
def web_search(query: str) -> str:
    """
    Performs a web search for the given query and returns a summary of results.
    In a real application, this would integrate with a robust search API like Serper, Tavily, etc.
    """
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = tavily_client.search(query)
    return response['results']

# Placeholder for a weather forecasting tool.
# In a real scenario, this would call a weather API (e.g., OpenWeatherMap).
def get_weather_forecast(location: str, start_date: str, end_date: str) -> str:
    """
    Fetches a simulated 5-day weather forecast for the given location and date.
    In a real application, this would integrate with a weather API like OpenWeatherMap.
    The date parameters should be in 'YYYY-MM-DD' format.
    """
    unit_group = 'metric'
    content_type = 'json'

    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{start_date}/{end_date}?unitGroup={unit_group}&contentType={content_type}&key={api_key}"
    api_key = tavilyKey

    try:
    # Request weather data from Visual Crossing Weather API
        with urllib.request.urlopen(url) as response:
            data = response.read()
            # Parse the returned JSON data
            weather_data = json.loads(data.decode('utf-8'))
            
            # Print out the results for inspection
            return(json.dumps(weather_data, indent=4))

    except urllib.error.HTTPError as e:
        # Handle HTTP errors
        error_message = e.read().decode('utf-8')
        return(f"HTTP Error: {e.code}, Message: {error_message}")
    except urllib.error.URLError as e:
        # Handle URL errors
        return(f"URL Error: {e.reason}")
    except Exception as e:
        # Handle any other exceptions
        return(f"Error: {str(e)}")

# --- Define the shared Gemini LLM configuration ---
gemini_llm_config = {
    "config_list": [
        {
            "model": "gemini-2.5-flash",
            "api_key": gemini_api_key,
            "api_type": "google",
        }
    ],
    "temperature": 0.7
}

# --- Create the agents ---

# The UserProxyAgent needs to know about the functions so it can execute them
# when an AssistantAgent recommends calling one.
user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="TERMINATE", # Set to "ALWAYS" or "TERMINATE" if you want human approval
    code_execution_config={
        "last_n_messages": 1, # Only consider the last message for code execution
        "work_dir": "coding", # Directory for generated code files
        "use_docker": False, # Set to True if you have Docker and want isolated execution
    },
    # The function_map explicitly tells the UserProxyAgent which Python functions it can execute.
    function_map={
        "web_search": web_search,
        "get_weather_forecast": get_weather_forecast,
        # Add any other tools here that the UserProxyAgent might need to execute
    },
    # It's generally good practice for the UserProxyAgent to have an LLM config
    # if it might need to generate replies when human input is not provided,
    # or if it's coordinating tool calls.
    llm_config=gemini_llm_config, # Let UserProxyAgent also use Gemini for its own reasoning
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") != -1, # Custom termination message
)


planner = AssistantAgent(
    name="PlannerAgent",
    llm_config=gemini_llm_config,
    system_message="""PlannerAgent. Your goal is to create a structured travel itinerary day-by-day given location, duration, and preferences.
    You can suggest initial ideas but rely on other agents for details. Once you have enough information, suggest the overall structure.
    """
)

researcher = AssistantAgent(
    name="ResearchAgent",
    llm_config=gemini_llm_config,
    system_message="""ResearchAgent. Your goal is to suggest restaurants, cultural spots, local experiences, and hidden gems for the given destination.
    You have access to the 'web_search' tool. Use it to find specific information when needed.
    Always present your findings clearly.
    """
)

coordinator = AssistantAgent(
    name="CoordinatorAgent",
    llm_config=gemini_llm_config,
    system_message="""CoordinatorAgent. Your goal is to combine inputs from PlannerAgent and ResearchAgent into one clear, executable travel plan.
    Ensure all preferences are met and the plan is logical.
    When the plan is complete, say 'TERMINATE'.
    """
)

forecaster = AssistantAgent(
    name="WeatherForecaster",
    llm_config=gemini_llm_config,
    system_message="""WeatherForecaster. Your goal is to give inputs on the weather over the span of the trip at the location specified.
    You have access to the 'get_weather_forecast' tool. Use it to retrieve specific weather information.
    Provide concise weather summaries.
    """
)

groupchat = GroupChat(
    agents=[user_proxy, planner, researcher, coordinator, forecaster],
    messages=[],
    max_round=12, # Increased max_round to allow for tool calls and more conversation
    speaker_selection_method="auto" # Let manager decide who speaks
)

manager = GroupChatManager(
    groupchat=groupchat,
    llm_config=gemini_llm_config
)

user_proxy.initiate_chat(
    manager,
    message="Plan a 5-day food and culture trip to Kyoto in April. I want to see historical sites, experience local food, and find some unique hidden gems. Also, tell me about the weather for that period."
)