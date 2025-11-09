# CompleteTravelAgentSystem

Lightweight multi-agent travel-planning system that coordinates planner, researcher, weather forecaster, calendar conversion, and calendar integration agents using the AutoGen-style orchestration in this repo.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Repository structure

- [CalendarIntegrated.py](CalendarIntegrated.py) - full pipeline with calendar event creation and delayed Gemini client. See [`CalendarIntegrated.create_delayed_gemini_client`](CalendarIntegrated.py) and [`CalendarIntegrated.add_calendar_event`](CalendarIntegrated.py).
- [DelayedGC.py](DelayedGC.py) - variant that demonstrates per-call delay and different Gemini model config. See [`DelayedGC.create_delayed_gemini_client`](DelayedGC.py).
- [groupAndTools.py](groupAndTools.py) - group chat setup with local tool implementations: [`groupAndTools.web_search`](groupAndTools.py) and [`groupAndTools.get_weather_forecast`](groupAndTools.py).
- [group.py](group.py) - simplified group chat example (no local tools implemented in this file).
- [main.py](main.py) - minimal Gemini-backed assistants and orchestration. See [`main.call_gemini`](main.py) and [`main.GeminiAssistant`](main.py).
- [tools.py](tools.py) - FastMCP calendar integration server and tool: [`tools.interactWithCalendar`](tools.py).
- [travel_plan.md](travel_plan.md) - example generated travel plan output.
- [.env](.env) - environment variables (should not be committed with secrets).
- [.gitignore](.gitignore) - ignores `.env`, virtual envs, and submission artifacts.
- [coding/](coding/) - working directory used by agents for generated code.

## Quick start

1. Create a virtual environment and install dependencies (example):
```sh
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt  # add a requirements.txt if needed
```

2. Populate environment variables. Do NOT commit secrets to git. The project expects:
- `GEMINI_API_KEY`
- `TAVILY_API_KEY`
- `CALENDAR_URL`

Add them to a local `.env` file (example entries, DO NOT paste real keys here). This repo currently contains a `.env` file but you should replace values with your own keys or remove the file before committing.

3. Run examples:
- Run the integrated pipeline (creates travel plan + calendar events):
```sh
python CalendarIntegrated.py
```
- Run delayed-call demonstration:
```sh
python DelayedGC.py
```
- Run simplified group demo:
```sh
python group.py
```
- Run the FastMCP calendar tool server:
```sh
python tools.py
```
- Run minimal orchestration using Gemini calls:
```sh
python main.py
```

## Tools and useful symbols

- Web / search tool: [`groupAndTools.web_search`](groupAndTools.py) ([groupAndTools.py](groupAndTools.py))
- Weather tool: [`groupAndTools.get_weather_forecast`](groupAndTools.py) ([groupAndTools.py](groupAndTools.py))
- Calendar REST wrapper: [`CalendarIntegrated.add_calendar_event`](CalendarIntegrated.py) ([CalendarIntegrated.py](CalendarIntegrated.py))
- FastMCP calendar tool: [`tools.interactWithCalendar`](tools.py) ([tools.py](tools.py))
- Delayed Gemini client builders: [`DelayedGC.create_delayed_gemini_client`](DelayedGC.py) ([DelayedGC.py](DelayedGC.py)), [`CalendarIntegrated.create_delayed_gemini_client`](CalendarIntegrated.py) ([CalendarIntegrated.py](CalendarIntegrated.py))
- Gemini helper & assistant: [`main.call_gemini`](main.py) and [`main.GeminiAssistant`](main.py) ([main.py](main.py))

## Notes & best practices

- Secrets: do not commit API keys. This repo's [.gitignore](.gitignore) already ignores `.env`.
- The repo includes multiple example entry points — pick the file that matches your needs:
  - Full integrated flow: [CalendarIntegrated.py](CalendarIntegrated.py)
  - Test / demo flows: [DelayedGC.py](DelayedGC.py), [group.py](group.py), [groupAndTools.py](groupAndTools.py)
  - Lower-level Gemini wrapper: [main.py](main.py)
- The calendar integration calls an Apps Script endpoint via `CALENDAR_URL`. Verify that endpoint and authentication before running the calendar tools.

## Contributing

- Add tests and a `requirements.txt`.
- Factor duplicated helpers (e.g., `web_search`, `get_weather_forecast`) into a shared module if you intend to maintain multiple demos.
- Sanitize any example `.env` files before pushing.

## License

This project is licensed under the MIT License — see the top-level `LICENSE` file for details.

```// filepath: README.md
# CompleteTravelAgentSystem

Lightweight multi-agent travel-planning system that coordinates planner, researcher, weather forecaster, calendar conversion, and calendar integration agents using the AutoGen-style orchestration in this repo.

## Repository structure

- [CalendarIntegrated.py](CalendarIntegrated.py) - full pipeline with calendar event creation and delayed Gemini client. See [`CalendarIntegrated.create_delayed_gemini_client`](CalendarIntegrated.py) and [`CalendarIntegrated.add_calendar_event`](CalendarIntegrated.py).
- [DelayedGC.py](DelayedGC.py) - variant that demonstrates per-call delay and different Gemini model config. See [`DelayedGC.create_delayed_gemini_client`](DelayedGC.py).
- [groupAndTools.py](groupAndTools.py) - group chat setup with local tool implementations: [`groupAndTools.web_search`](groupAndTools.py) and [`groupAndTools.get_weather_forecast`](groupAndTools.py).
- [group.py](group.py) - simplified group chat example (no local tools implemented in this file).
- [main.py](main.py) - minimal Gemini-backed assistants and orchestration. See [`main.call_gemini`](main.py) and [`main.GeminiAssistant`](main.py).
- [tools.py](tools.py) - FastMCP calendar integration server and tool: [`tools.interactWithCalendar`](tools.py).
- [travel_plan.md](travel_plan.md) - example generated travel plan output.
- [.env](.env) - environment variables (should not be committed with secrets).
- [.gitignore](.gitignore) - ignores `.env`, virtual envs, and submission artifacts.
- [coding/](coding/) - working directory used by agents for generated code.

## Quick start

1. Create a virtual environment and install dependencies (example):
```sh
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt  # add a requirements.txt if needed
```

2. Populate environment variables. Do NOT commit secrets to git. The project expects:
- `GEMINI_API_KEY`
- `TAVILY_API_KEY`
- `CALENDAR_URL`

Add them to a local `.env` file (example entries, DO NOT paste real keys here). This repo currently contains a `.env` file but you should replace values with your own keys or remove the file before committing.

3. Run examples:
- Run the integrated pipeline (creates travel plan + calendar events):
```sh
python CalendarIntegrated.py
```
- Run delayed-call demonstration:
```sh
python DelayedGC.py
```
- Run simplified group demo:
```sh
python group.py
```
- Run the FastMCP calendar tool server:
```sh
python tools.py
```
- Run minimal orchestration using Gemini calls:
```sh
python main.py
```

## Tools and useful symbols

- Web / search tool: [`groupAndTools.web_search`](groupAndTools.py) ([groupAndTools.py](groupAndTools.py))
- Weather tool: [`groupAndTools.get_weather_forecast`](groupAndTools.py) ([groupAndTools.py](groupAndTools.py))
- Calendar REST wrapper: [`CalendarIntegrated.add_calendar_event`](CalendarIntegrated.py) ([CalendarIntegrated.py](CalendarIntegrated.py))
- FastMCP calendar tool: [`tools.interactWithCalendar`](tools.py) ([tools.py](tools.py))
- Delayed Gemini client builders: [`DelayedGC.create_delayed_gemini_client`](DelayedGC.py) ([DelayedGC.py](DelayedGC.py)), [`CalendarIntegrated.create_delayed_gemini_client`](CalendarIntegrated.py) ([CalendarIntegrated.py](CalendarIntegrated.py))
- Gemini helper & assistant: [`main.call_gemini`](main.py) and [`main.GeminiAssistant`](main.py) ([main.py](main.py))

## Notes & best practices

- Secrets: do not commit API keys. This repo's [.gitignore](.gitignore) already ignores `.env`.
- The repo includes multiple example entry points — pick the file that matches your needs:
  - Full integrated flow: [CalendarIntegrated.py](CalendarIntegrated.py)
  - Test / demo flows: [DelayedGC.py](DelayedGC.py), [group.py](group.py), [groupAndTools.py](groupAndTools.py)
  - Lower-level Gemini wrapper: [main.py](main.py)
- The calendar integration calls an Apps Script endpoint via `CALENDAR_URL`. Verify that endpoint and authentication before running the calendar tools.

## Contributing

- Add tests and a `requirements.txt`.
- Factor duplicated helpers (e.g., `web_search`, `get_weather_forecast`) into a shared module if you intend to maintain multiple demos.
- Sanitize any example `.env` files before pushing.
