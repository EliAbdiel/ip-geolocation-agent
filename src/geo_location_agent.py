import os
import requests
import chainlit as cl
from dotenv import load_dotenv
from agents import (
    Agent,
    # Runner,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
    AsyncOpenAI,
    function_tool
)
from dataclasses import dataclass

load_dotenv()

set_tracing_disabled(disabled = True)

base_url = os.environ["GEMINI_ENDPOINT"]
api_key = os.environ["GEMINI_API_KEY_V2"]
model = os.environ["GEMINI_MODEL"]

provider = AsyncOpenAI(
    base_url = base_url,
    api_key = api_key
)

MODEL = OpenAIChatCompletionsModel(
    model = model,
    openai_client = provider
)

@dataclass
class LocationInfo:
    ip: str
    city: str
    region: str
    country: str
    latitude: float
    longitude: float
    timezone: str
    org:str

    def __str__(self):
        """Return a formatted string representation of the location info."""
        return f"""📡 **IP Geolocation Info**
        - 🌐 IP: `{self.ip}`
        - 🏙 City: **{self.city}**, {self.region}
        - 🌍 Country: **{self.country}**
        - 📍 Location: `{self.latitude}, {self.longitude}`
        - 🕒 Timezone: `{self.timezone}`
        - 🏢 Organization: {self.org}
        """
    
@function_tool
async def get_location_info(ip: str) -> LocationInfo:
    """
    Fetches geolocation information for a given IP address.
    
    Args:
        ip (str): The IP address to look up.
        
    Returns:
        LocationInfo: A dataclass containing the geolocation details.
    """

    url = f"https://ipapi.co/{ip or ''}/json/"
    response = requests.get(url)
    data = response.json()

    return LocationInfo(
        ip=data.get("ip", "N/A"),
        city=data.get("city", "N/A"),
        region=data.get("region", "N/A"),
        country=data.get("country", "N/A"),
        latitude=float(data.get("loc", "0,0").split(",")[0]),
        longitude=float(data.get("loc", "0,0").split(",")[1]),
        timezone=data.get("timezone", "N/A"),
        org=data.get("org", "N/A")
    )

async def get_agent():
    """Create and return the GeoLocation Agent."""
    agent = Agent(
        name="GeoLocationAgent",
        instructions="You are a helpful agent, if the user ask about gelocation of ip addresses use tool 'get_location_info' and return a formated beutiful output using LocationInfo dataclass.",
        model=MODEL,
        tools=[get_location_info],
        output_type=LocationInfo,
        tool_use_behavior="required",)
    
    return agent