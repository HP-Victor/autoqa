import asyncio
import os
from agents import Agent, ModelSettings, Runner

MAX_TURNS = int(os.environ.get("MAX_TURNS", 100))
PROMPT = os.environ.get("PROMPT")

if not PROMPT:
    raise ValueError("PROMPT environment variable is not set")

# Elegir modelo desde variable de entorno
MODEL = os.environ.get("OPENAI_MODEL", "gpt-5-pro")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Determinar si es modelo de Claude o OpenAI
if "claude" in MODEL.lower():
    if not ANTHROPIC_API_KEY:
        raise ValueError("Anthropic API key required for Claude models. Set ANTHROPIC_API_KEY")
    print(f"✅ Using Claude model for code generation: {MODEL}")
else:
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key required for OpenAI models. Set OPENAI_API_KEY")
    print(f"✅ Using OpenAI model for code generation: {MODEL}")

# Crear agente
agent = Agent(
    model=MODEL,
    model_settings=ModelSettings(truncation="auto", reasoning={"summary": "auto"}),
    name="Code Generator Agent",
    instructions=PROMPT
)

# Ejecutar agente
async def main():
    result = Runner.run_streamed(agent, PROMPT, max_turns=MAX_TURNS)

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
