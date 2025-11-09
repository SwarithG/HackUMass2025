import os
from dotenv import load_dotenv
from autogen import GroupChat, GroupChatManager, AssistantAgent, UserProxyAgent
import json # For handling JSON responses
import requests # For making HTTP requests to external APIs (e.g., weather, search)
from tavily import TavilyClient
import urllib.request
import json
import datetime

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
    Fetches a simulated 5-day weather forecast for the given location (city) and date range.
    In a real application, this would integrate with a weather API like OpenWeatherMap.
    The date parameters should be in 'YYYY-MM-DD' format.
    eg. - location:Kyoto , start_end:2025-04-05 , end_date: 2025-04-10
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

def add_calendar_event(
    title: str,
    start_time: datetime.datetime,
    end_time: datetime.datetime
) -> dict:
    """
    Makes a request to the Google Apps Script web app to create a new calendar event.

    Args:
        title: The title of the event.
        start_time: A datetime object representing the event's start time.
        end_time: A datetime object representing the event's end time.

    Returns:
        A dictionary containing the JSON response from the Apps Script.
    """
    # Format datetime objects to ISO 8601 strings, which JavaScript Date constructor can parse
    start_time_iso = start_time.isoformat()
    end_time_iso = end_time.isoformat()

    payload = {
        "function_name": "createEvent",
        "arguments": {
            "calendarId": "primary",
            "title": title,
            "startTime": start_time_iso,
            "endTime": end_time_iso
        }
    }

    headers = {
        "Content-Type": "application/json"
    }
    url = os.getenv("CALENDAR_URL")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request to Apps Script: {e}")
        return {"error": str(e)}

LLM_CALL_DELAY_SECONDS = 15

def create_delayed_gemini_client(config):
    """
    Custom client builder that injects a delay before each Gemini API call.
    This function patches the global `genai.GenerativeModel.generate_content` method
    to include a `time.sleep()`.
    """
    # The global genai.configure(api_key=api_key) should handle this,
    # but we can add a fallback check here if needed.
    # if not genai.types.Client.api_key and config.get("api_key"):
    #     genai.configure(api_key=config.get("api_key"))

    # Only patch the method once globally
    if not hasattr(genai.GenerativeModel, '_original_generate_content'):
        genai.GenerativeModel._original_generate_content = genai.GenerativeModel.generate_content

        def delayed_generate_content_wrapper(self, *args, **kwargs):
            print(f"--- [LLM Call Delay: Sleeping for {LLM_CALL_DELAY_SECONDS} seconds] ---")
            time.sleep(LLM_CALL_DELAY_SECONDS)
            return genai.GenerativeModel._original_generate_content(self, *args, **kwargs)

        genai.GenerativeModel.generate_content = delayed_generate_content_wrapper

    # Create and return the Gemini model instance (it will now use the patched method)
    model_name = config.get("model", "gemini-2.0-flash")
    return genai.GenerativeModel(model_name=model_name)

# --- Define the shared Gemini LLM configuration ---
gemini_llm_config = {
    "config_list": [
        {
            "model": "gemini-2.0-flash",
            "api_key": gemini_api_key,
            "api_type": "google",
            "custom_client_builder": create_delayed_gemini_client, # Link our custom builder here
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
        "add_calendar_event": add_calendar_event
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
    Suggest initial ideas and an overall geographical structure. Do NOT add specific restaurant or weather details; rely on ResearchAgent and WeatherForecaster for that.
    """
)

researcher = AssistantAgent(
    name="ResearchAgent",
    llm_config=gemini_llm_config,
    system_message="""ResearchAgent. Your goal is to suggest specific restaurants, cultural spots, local experiences, and hidden gems for the given destination,
    aligned with the PlannerAgent's daily structure and user's preferences (food, culture, hidden gems).
    You have access to the 'web_search' tool. **You MUST use 'web_search' whenever you need specific, up-to-date, or detailed information** about places, activities, or food recommendations.
    Always present your findings clearly, *after* using the tool, and mention what you searched for and what you found. If the PlannerAgent provides a day's theme, elaborate on it using your research tool.
    """
)

coordinator = AssistantAgent(
    name="CoordinatorAgent",
    llm_config=gemini_llm_config,
    system_message="""CoordinatorAgent. Your goal is to synthesize and combine all inputs from PlannerAgent, ResearchAgent, and WeatherForecaster into one clear, comprehensive, and executable travel plan.
    **Do NOT create a detailed itinerary until PlannerAgent has provided a full daily structure, ResearchAgent has provided specific recommendations, and WeatherForecaster has provided the official forecast.**
    Ensure all user preferences are met, the plan is logical, and weather considerations are integrated.
    Present the full, final itinerary clearly, and then explicitly say 'TERMINATE' to signal completion.
    """
)

forecaster = AssistantAgent(
    name="WeatherForecaster",
    llm_config=gemini_llm_config,
    system_message="""WeatherForecaster. Your primary goal is to provide the definitive weather forecast for the trip's location and dates.
    **You MUST call the 'get_weather_forecast' tool first, for the specified location (e.g., 'Kyoto') and full date range (e.g., '2024-04-01', '2024-04-05').**
    **After the tool executes and provides its output, you MUST then clearly and concisely summarize the *tool's exact findings* for the group in your next message.**
    Do not assume weather or rely on other agents' weather information; use your tool to get the most accurate data. Be explicit about the forecast.
    """
)

converter = AssistantAgent(
    name="CalendarFormConverter",
    llm_config=gemini_llm_config,
    system_message="""CalendarFormConverter. Your primary goal is to convert the finalized travel plan into a realistic scheulde.
    Your role is to take the approved travel plan and make the plan into a schedule deciding the timings and order of events as outlined in the plan.
    You are to then create a final calendar form version of the plan where each event has location and time specified and this information is to be written to calform.md
    Then proceed to hand over the chat to the CalendarIntegrater to add events to calendar next."""
)

integrater = AssistantAgent(
    name="CalendarIntegrater",
    llm_config=gemini_llm_config,
    system_message="""CalendarIntegrater. Your primary goal is take the coverted form of the travel plan given by the CalendarFormConverter
     and then use the add_calendar_event tool to add the events to the traveller's calendar. Your role is to make sure the traveller's calendar has the 
      confirmed schedule. You are then to reply whether the adding of all the events worked and when all the events have been added reply with TERMINATE to signal to the 
       groupchatManager that the plan has been added to calendar. """
)

groupchat = GroupChat(
    agents=[user_proxy, planner, researcher, coordinator, forecaster,converter,integrater],
    messages=[],
    max_round=30, # Increased max_round to allow for tool calls and more conversation
    speaker_selection_method="auto" # Let manager decide who speaks
)

manager = GroupChatManager(
    groupchat=groupchat,
    llm_config=gemini_llm_config
)

try:
    print(f"\n--- Starting chat with per-LLM-call delay of {LLM_CALL_DELAY_SECONDS} seconds ---\n")
    chat_result = user_proxy.initiate_chat(
        manager,
        message="Plan a 5-day food and culture trip to Kyoto in December from December 20th to December 25th 2025. I want to see historical sites, experience local food, and find some unique hidden gems. Also, take into account the weather for the activites."
    )
    print("\n--- Chat completed ---")

    # Corrected extraction of the last message and plan
    # Check if there's any chat history at all
    if chat_result.chat_history:
        # Get the very last message from the chat history
        last_message = chat_result.chat_history[-2]

        # Check if the last message content is "TERMINATE"
        if last_message.get("content", "").strip() == "TERMINATE":
            print("\n--- Termination signal received, extracting final plan ---")
            final_plan_content = ""
            # Iterate through chat history in reverse, excluding the final TERMINATE message
            for i in range(len(chat_result.chat_history) - 2, -1, -1): # Start from second to last
                msg = chat_result.chat_history[i]
                # Look for a message from CoordinatorAgent that is not just "TERMINATE"
                if msg.get("sender") == "CoordinatorAgent" and msg.get("content") and msg["content"].strip() != "TERMINATE":
                    final_plan_content = msg["content"]
                    break

            if final_plan_content:
                file_name = "kyoto_travel_plan.md"
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(f"\t -> Travel Plan <-\n\n")
                    f.write(final_plan_content)
                print(f"\nTravel plan saved successfully to {file_name}")
            else:
                print("\nCould not find a comprehensive plan from CoordinatorAgent before termination.")
        else:
            print("\nChat terminated, but the last message was not an explicit 'TERMINATE'.")
            print("Last message content:", last_message.get("content", "N/A"))
            file_name = "travel_plan.md"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(f"\t -> Travel Plan <-\n\n")
                f.write(last_message.get("content","N/A"))
            print(f"\nTravel plan saved successfully to {file_name}")
    else:
        print("\nChat history is empty.")


except Exception as e:
    print(f"\n--- An unexpected error occurred during chat initiation: {e} ---")
    raise