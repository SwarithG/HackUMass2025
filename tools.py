from typing import Any
import httpx
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os

# Initialize FastMCP server
mcp = FastMCP("CalendarIntegration")

# Load the env variables
load_dotenv()
url = os.getenv("URL")


@mcp.tool()
async def interactWithCalendar(funcName : str,arguments):
    """
    Add any two numbers by performing simple addition
    Args: 
        funcName : The name of the function to be invoked
        arguments :The required arguments in the form of a JSON object for the selected function.
    Functions Available:
        {
  "tools": [
    {
      "name": "getUpcomingEvents",
      "description": "Gets a list of upcoming events from all the user's calendars.",
      "parameters": {
        "type": "object",
        "properties": {}
      }
    },
    {
      "name": "searchEventsByTime",
      "description": "Retrieves all calendar events within a specified time period from a specific calendar. The calendar can be specified by its ID; otherwise, the user's default calendar is used.",
      "parameters": {
        "type": "object",
        "properties": {
          "startTime": {
            "type": "string",
            "description": "The start time of the period in ISO 8601 format."
          },
          "endTime": {
            "type": "string",
            "description": "The end time of the period in ISO 8601 format."
          },
          "calendarId": {
            "type": "string",
            "description": "The ID of the calendar to search. This is optional; if not provided, the default calendar is used."
          }
        },
        "required": [
          "startTime",
          "endTime"
        ]
      }
    },
    {
      "name": "getCalendarList",
      "description": "Retrieves a list of all the user's calendars with their IDs and names.",
      "parameters": {
        "type": "object",
        "properties": {}
      }
    },
    {
      "name": "createEvent",
      "description": "Creates a new calendar event on a specific calendar.",
      "parameters": {
        "type": "object",
        "properties": {
          "calendarId": {
            "type": "string",
            "description": "The unique ID of the calendar to add the event to."
          },
          "title": {
            "type": "string",
            "description": "The title of the event."
          },
          "startTime": {
            "type": "string",
            "format": "date-time",
            "description": "The start time of the event in ISO 8601 format."
          },
          "endTime": {
            "type": "string",
            "format": "date-time",
            "description": "The end time of the event in ISO 8601 format."
          }
        },
        "required": ["calendarId", "title", "startTime", "endTime"]
      }
    },
    {
      "name": "deleteEvent",
      "description": "Deletes an existing event from a specified calendar.",
      "parameters": {
        "type": "object",
        "properties": {
          "calendarId": {
            "type": "string",
            "description": "The ID of the calendar the event is on."
          },
          "eventId": {
            "type": "string",
            "description": "The unique ID of the event to delete."
          }
        },
        "required": ["calendarId", "eventId"]
      }
    },
    {
      "name": "moveEvent",
      "description": "Moves an event from one calendar to another.",
      "parameters": {
        "type": "object",
        "properties": {
          "eventId": {
            "type": "string",
            "description": "The unique ID of the event to move."
          },
          "sourceCalendarId": {
            "type": "string",
            "description": "The ID of the calendar the event is currently on."
          },
          "destinationCalendarId": {
            "type": "string",
            "description": "The ID of the calendar to move the event to."
          }
        },
        "required": ["eventId", "sourceCalendarId", "destinationCalendarId"]
      }
    },
    {
      "name": "readEventData",
      "description": "Reads the detailed data for a single calendar event.",
      "parameters": {
        "type": "object",
        "properties": {
          "calendarId": {
            "type": "string",
            "description": "The ID of the calendar the event is on."
          },
          "eventId": {
            "type": "string",
            "description": "The unique ID of the event."
          }
        },
        "required": ["calendarId", "eventId"]
      }
    },
    {
      "name": "modifyEventData",
      "description": "Modifies the title, time, or location of an existing event.",
      "parameters": {
        "type": "object",
        "properties": {
          "calendarId": {
            "type": "string",
            "description": "The ID of the calendar the event is on."
          },
          "eventId": {
            "type": "string",
            "description": "The unique ID of the event to modify."
          },
          "updates": {
            "type": "object",
            "description": "A JSON object containing the fields to update (title, startTime, endTime, etc.)."
          }
        },
        "required": ["calendarId", "eventId"]
      }
    }
  ]
}
        """
    data = {
    "function_name": funcName,
    "arguments": arguments,
}
    
    response = requests.post(url, json=data)

    return  response.json()


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')