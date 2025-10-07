import asyncio
import os
from agents import Agent, ModelSettings, Runner

MAX_TURNS = int(os.environ.get("MAX_TURNS", 100))
PROMPT = os.environ.get("PROMPT")

if not PROMPT:
    raise ValueError("PROMPT environment variable is not set")

# Elegir modelo: solo OpenAI GPT-5/pro porque no necesitamos ejecutar nada
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5-pro")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("No OpenAI API key found. Set OPENAI_API_KEY")

MODEL = OPENAI_MODEL
print(f"✅ Using OpenAI GPT-5 for code generation: {MODEL}")

# Crear agente
agent = Agent(
    model=MODEL,
    model_settings=ModelSettings(truncation="auto", reasoning={"summary": "auto"}),
    name="Code Generator Agent",
    instructions=PROMPT
)

# Ejecutar agente
async def main():
    result = Runner.run_streamed(agent, PROMPT, max_turns=MAX_TURNS,stream=False)

    async for event in result.stream_events():
        if hasattr(event, "type") and event.type == "raw_response_event":
            data = event.data
            if hasattr(data, "type") and data.type == "response.reasoning_summary_text.done":
                print(f"🧠 Agent reasoning: {data.text}")

    print(f"📝 Generated code output:\n{result.final_output}")

if __name__ == "__main__":
    print("Starting AutoQA code generation...")
    asyncio.run(main())
    print("Done")
