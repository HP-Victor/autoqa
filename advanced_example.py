import asyncio
import json
from typing import Dict, List
from agents import Agent, Runner, Tool

# Define a calculator tool
class CalculatorTool(Tool):
    """A tool for performing basic calculations."""
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        """Divide a by b."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

# Create a calculator tool instance
calculator = CalculatorTool()

# Create an agent with the calculator tool
math_agent = Agent(
    name="Advanced Math Tutor",
    instructions="""You are a helpful math tutor that can solve complex problems.
    Use the calculator tool when you need to perform precise calculations.
    Show your work and explain each step clearly.""",
    tools=[calculator]
)

async def main():
    print("Initializing Advanced Math Tutor agent...")
    
    # Run the agent with a complex problem
    result = await Runner.run(
        math_agent, 
        "Solve this problem: If I have $1250 and want to invest it with a 7.5% annual return, how much will I have after 5 years? Please use the calculator tool."
    )
    
    print(f"Response: {result.final_output}")

if __name__ == "__main__":
    asyncio.run(main())