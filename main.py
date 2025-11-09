from autogen import UserProxyAgent
import google.generativeai as genai
from autogen import AssistantAgent
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def call_gemini(prompt: str) -> str:
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text

class GeminiAssistant(AssistantAgent):
    def __init__(self, name, role_description):
        super().__init__(name=name)
        self.role_description = role_description

    def generate_reply(self, messages, sender=None):
        # Combine messages into a prompt
        prompt = "\n".join([m["content"] for m in messages if "content" in m])
        # Call Gemini
        reply = call_gemini(prompt)
        # Return in the format AutoGen expects
        return {"content": reply}

# Create the agents
user = UserProxyAgent(
    name="User",
    code_execution_config={"use_docker": False}
)

planner = GeminiAssistant(
    name="PlannerAgent",
    role_description="Create structured travel itineraries day-by-day given location and duration."
)

researcher = GeminiAssistant(
    name="ResearchAgent",
    role_description="Suggest restaurants, cultural spots, local experiences, and hidden gems for the given destination."
)

coordinator = GeminiAssistant(
    name="CoordinatorAgent",
    role_description="Combine inputs from PlannerAgent and ResearchAgent into one clear, executable travel plan."
)

# assistant = GeminiAssistant(name="GeminiAgent")

# Start the chat
initial_message = "Plan a 5-day trip to Kyoto in April focused on food and culture."

# Step 1: Planner creates base plan
planner_reply = planner.generate_reply([{"content": initial_message}])["content"]

# Step 2: Researcher adds local recommendations
researcher_reply = researcher.generate_reply([
    {"content": f"Destination info from PlannerAgent:\n{planner_reply}"}
])["content"]

# Step 3: Coordinator merges everything
final_plan = coordinator.generate_reply([
    {"content": f"Planner's itinerary:\n{planner_reply}\n\nResearcher's input:\n{researcher_reply}"}
])["content"]

print("✅ Final AI-generated Travel Plan:\n")
print(final_plan)