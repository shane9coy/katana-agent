---
name: weather
description: Fetch current weather via Open-Meteo using the user's location from user_profile.json. Always deliver warm, contextual, actionable advice (never raw numbers).
---

## Weather Skill

**When to use this skill**  
Any time the user asks about the weather, temperature, forecast, “is it nice out?”, what to wear, outdoor plans, etc.

**Core workflow (always follow exactly)**

1. **Read location**  
   Use `read_file` to load `~/.katana/defaults/user_profile.json'(check project root first, then `~/.config/kilo/user_profile.json` or `~/user_profile.json`).

   Expected structure:
   ```json
  "location": {
    "latitude":,
    "longitude":,
    "city":,
    "state":,
    "country":,
    "timezone":
  },
    ```

Fetch data (no API key needed)
Run this bash command (replace ${LAT} and ${LON}):Bashcurl -s "https://api.open-meteo.com/v1/forecast?latitude=${LAT}&longitude=${LON}&current_weather=true&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto"
Interpret & contextualize
Turn raw temp + weathercode into a human-friendly summary.
Never just say the temperature.
Always add real-life impact and friendly advice.


Exact tone & style you must match

"72 and clear — good day to work outside if you need a reset."
"Rain all afternoon — cancel that outdoor lunch plan."
"61° and overcast, light wind. Comfortable for a run but you’ll want a light layer."

Bonus examples

“48° and pouring in Sandusky — definitely cancel that outdoor lunch plan and stay in to code.”
“Clear skies, 72°F, light breeze — perfect reset day. Go touch grass after you ship that PR.”
“High of 55° with 80% chance of afternoon showers — morning is dry if you want to grab coffee outside.”

Pro tips for the agent

Mention city name when relevant.
Include short-term outlook (afternoon/evening) if the user might care.
Keep it warm, concise, and useful — like a helpful local friend.