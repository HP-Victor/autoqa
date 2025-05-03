import asyncio
from agents import Agent, ComputerTool, ModelSettings, Runner
from openai.types.responses import ResponseTextDeltaEvent
from execute import VM
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found in environment variables")
    print("Please set your OpenAI API key in the .env file or environment")


computer = VM(display=":99", container_name="computer")

math_agent = Agent(
    model="computer-use-preview",
    model_settings=ModelSettings(
        truncation="auto",
        reasoning={"summary": "concise"},
    ),
    name="Computer User",
    instructions="""You are a helpful assistant that can control a computer.
    You have access to a virtual machine running Ubuntu.
    You can take screenshots, click, type, scroll, and perform other computer operations.
    When asked to perform tasks, use the computer tool to interact with the GUI environment.
    Explain what you're doing as you complete tasks.""",
    tools=[ComputerTool(computer)],
)


async def main():
    print("Initializing Advanced Math Tutor agent...")

    # Run the agent with a complex problem
    result = await Runner.run(
        math_agent,
        "Visit https://mitchellhynes.com/ and see if it works.",
    )

    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            print(event.data.delta, end="", flush=True)

    print(f"Response: {result.final_output}")


if __name__ == "__main__":
    print("Starting AutoQA...")
    asyncio.run(main())

print("Done")
