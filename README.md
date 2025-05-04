# AutoQA

A tool that uses OpenAI Agents to control a virtual Ubuntu environment and perform automated QA testing.

## Setup

### Local Setup with Virtual Environment

## Prerequisites

This tool requires a VNC (Virtual Network Computing) server running on localhost:5900.

VNC is a graphical desktop-sharing system that allows you to remotely control another computer. The tool connects to this VNC server to interact with a virtual Ubuntu environment.

By default, the application is configured to connect to:

- Host: localhost
- Port: 5900
- Username: ubuntu
- Password: secret

**If there is no application configured on localhost:5900 the script won't work.**

### Setup:

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set your OpenAI API key in a .env file:

   ```bash
   echo "OPENAI_API_KEY=your-api-key" > .env
   ```

## Running the Demo

Run the main script:

```bash
python autoqa.py
```

## Documentation

- [OpenAI Agents Python documentation](https://openai.github.io/openai-agents-python/)
- This project uses Docker to create a virtual Ubuntu environment with Xfce desktop
- The `execute.py` module provides a VM class that extends the Agent Computer to interact with the Docker container
