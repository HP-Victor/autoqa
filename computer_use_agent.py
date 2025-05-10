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

if not VNC_HOST:
    print("Warning: VNC_HOST not found in environment variables")
if not VNC_PORT:
    print("Warning: VNC_PORT not found in environment variables")
if not VNC_PASSWORD:
    print("Warning: VNC_PASSWORD not found in environment variables")

computer = VNCComputer(
    host=VNC_HOST if VNC_HOST is not None else "localhost",
    username="ubuntu",
    port=int(VNC_PORT) if VNC_PORT is not None else 5900,
    password=VNC_PASSWORD
)

computer_use_agent = Agent(
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
