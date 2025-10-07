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

VNC_HOST = os.getenv("VNC_HOST")
VNC_PORT = os.getenv("VNC_PORT")
VNC_PASSWORD = os.getenv("VNC_PASSWORD")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Modelos que soportan computer use
COMPUTER_USE_MODELS = ['gpt-4o', 'gpt-4o-2024-08-06', 'gpt-4o-2024-11-20']

if not VNC_HOST:
    print("Warning: VNC_HOST not found in environment variables")
if not VNC_PORT:
    print("Warning: VNC_PORT not found in environment variables")
if not VNC_PASSWORD:
    print("Warning: VNC_PASSWORD not found in environment variables")

print(f"Using OpenAI model: {OPENAI_MODEL}")

# Validar si el modelo soporta computer use
if OPENAI_MODEL not in COMPUTER_USE_MODELS:
    print(f"❌ ERROR: Model '{OPENAI_MODEL}' does not support computer use tools.")
    print(f"✅ Supported models: {', '.join(COMPUTER_USE_MODELS)}")
    print("💡 Please use 'gpt-4o' or upgrade your OpenAI plan to access computer use features.")
    print(f"🔄 Original ecumene/autoqa probably used an older OpenAI API version.")
    print(f"📅 Current OpenAI policy (2024-2025) restricts computer use to premium models only.")
    raise ValueError(f"Model '{OPENAI_MODEL}' does not support computer use tools. Use gpt-4o instead.")

computer = VNCComputer(
    host=VNC_HOST if VNC_HOST is not None else "localhost",
    username="ubuntu",
    port=int(VNC_PORT) if VNC_PORT is not None else 5900,
    password=VNC_PASSWORD
)

computer_use_agent = Agent(
    model=OPENAI_MODEL,
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
