from agents import Runner
import chainlit as cl
from src.geo_location_agent import LocationInfo, get_agent

@cl.on_chat_start
async def on_chat_start():
    """Greet the user when the chat starts."""
    await cl.Message("Hello! I'm your GeoLocation Agent 🌍. Want to know the location of an IP address? Ask me!").send()

    agent = await get_agent()

    cl.user_session.set("history", [])
    cl.user_session.set("agent", agent)

@cl.on_message
async def handle_message(message: cl.Message):
    """Handle user messages and interact with the agent."""
    history = cl.user_session.get("history", [])
    history.append({"role": "user", "content": message.content})
    cl.user_session.set("history", history)
    agent = cl.user_session.get("agent", None)

    # Run the agent with the user's message
    result = await Runner.run(agent, input=history)
    output = result.final_output
    if isinstance(output, LocationInfo):
        # Format the output using the LocationInfo dataclass
        await cl.Message(content=str(output)).send()
    else:
        await cl.Message("Sorry, I couldn't retrieve the geolocation information.").send()