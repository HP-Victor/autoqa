import asyncio
from agents import Runner
import os
from computer_use_agent import computer_use_agent

MAX_TURNS = os.environ.get("MAX_TURNS", 100)
PROMPT = os.environ.get("PROMPT")

if PROMPT is None:
    raise ValueError("PROMPT environment variable is not set")

async def main():
    print("Initializing Advanced Math Tutor agent...")

    result = Runner.run_streamed(
        computer_use_agent,
        PROMPT,
        max_turns=MAX_TURNS,
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
