import asyncio
from agents import Agent, ComputerTool, ModelSettings, Runner
import os
from dotenv import load_dotenv

from computers.vnc import VNCComputer

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found in environment variables")
    print("Please set your OpenAI API key in the .env file or environment")


computer = VNCComputer(
    host="localhost", username="ubuntu", port=5900, password="secret"
)

math_agent = Agent(
    model="computer-use-preview",
    model_settings=ModelSettings(
        truncation="auto",
        reasoning={"summary": "auto"},
    ),
    name="Computer User",
    instructions="""You are a helpful assistant that can control a computer.
    You have access to a virtual machine running Ubuntu.
    You can take screenshots, click, type, scroll, and perform other computer operations.
    When asked to perform tasks, use the computer tool to interact with the GUI environment.
    You have full access to the computer, including the ability to install packages.
    Explain what you're doing as you complete tasks.""",
    tools=[ComputerTool(computer)],
)


async def main():
    print("Initializing Advanced Math Tutor agent...")

    result = Runner.run_streamed(
        math_agent,
        "Open firefox and go to mitchellhynes.com",
        max_turns=100,
    )

    async for event in result.stream_events():
        if hasattr(event, "type"):
            event_type = event.type

            if event_type == "raw_response_event":
                data = event.data
                if hasattr(data, "type"):
                    if data.type == "response.reasoning_summary_text.done" and hasattr(
                        data, "text"
                    ):
                        print(f"🧠 Agent reasoning: {data.text}")

    print(f"Response: {result.final_output}")


if __name__ == "__main__":
    print("Starting AutoQA...")
    asyncio.run(main())

print("Done")
