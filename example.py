import asyncio
import os
from dotenv import load_dotenv
from agents import Agent, Runner

# Load environment variables from .env file
load_dotenv()

# Create a simple agent
agent = Agent(
    name="Math Tutor",
    instructions="You provide help with math problems. Be clear and concise in your explanations."
)

async def main():
    print("Initializing Math Tutor agent...")
    result = await Runner.run(agent, "Solve 3x + 5 = 14")
    print(f"Response: {result.final_output}")

# Run the async function
if __name__ == "__main__":
    asyncio.run(main())