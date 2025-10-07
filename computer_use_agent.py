import asyncio
from agents import Agent, ComputerTool, ModelSettings, Runner
import os
from dotenv import load_dotenv

from computers.vnc import VNCComputer

load_dotenv()

# REALIDAD: OpenAI ha descontinuado computer_use_preview completamente
# SOLUCIÓN: Usar Anthropic Claude que SÍ tiene computer use funcionando

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Variables VNC
VNC_HOST = os.getenv("VNC_HOST")
VNC_PORT = os.getenv("VNC_PORT")
VNC_PASSWORD = os.getenv("VNC_PASSWORD")

if not VNC_HOST:
    print("Warning: VNC_HOST not found in environment variables")
if not VNC_PORT:
    print("Warning: VNC_PORT not found in environment variables")
if not VNC_PASSWORD:
    print("Warning: VNC_PASSWORD not found in environment variables")

# Determinar qué modelo usar
if ANTHROPIC_API_KEY:
    # OPCIÓN 1: Usar Claude (RECOMENDADO - computer use funciona)
    MODEL = "claude-3-5-sonnet-20241022"
    print(f"✅ Using Anthropic Claude: {MODEL}")
    print(f"🎯 Claude has working computer use capabilities!")
    API_TYPE = "anthropic"
elif OPENAI_API_KEY:
    # OPCIÓN 2: OpenAI (ADVERTENCIA - no tiene computer use)
    MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    print(f"⚠️  Using OpenAI: {MODEL}")
    print(f"❌ WARNING: OpenAI models NO LONGER support computer_use_preview")
    print(f"� This will FAIL. Please set ANTHROPIC_API_KEY instead.")
    API_TYPE = "openai"
else:
    print(f"❌ ERROR: No API key found!")
    print(f"✅ Set ANTHROPIC_API_KEY (recommended) for computer use")
    print(f"⚠️  Or set OPENAI_API_KEY (but computer use won't work)")
    raise ValueError("No API key available")

# Configurar VNC Computer
computer = VNCComputer(
    host=VNC_HOST if VNC_HOST is not None else "localhost",
    username="ubuntu",
    port=int(VNC_PORT) if VNC_PORT is not None else 5900,
    password=VNC_PASSWORD
)

# Crear agente
try:
    computer_use_agent = Agent(
        model=MODEL,
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
    print(f"✅ Agent initialized successfully with {API_TYPE}")
    
    if API_TYPE == "openai":
        print(f"⚠️  WARNING: This agent will likely fail due to OpenAI computer use limitations")
        
except Exception as e:
    print(f"❌ Failed to initialize agent: {e}")
    if API_TYPE == "openai" and "computer_use" in str(e):
        print(f"💡 EXPECTED: OpenAI no longer supports computer use")
        print(f"🔧 SOLUTION: Set ANTHROPIC_API_KEY to use Claude instead")
    raise
