# AutoQA

A tool that uses OpenAI Agents to control a virtual Ubuntu environment and perform automated QA testing.

## Setup

### Option 1: Local Setup with Virtual Environment

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

4. Build and start the computer:

   ```bash
   docker-compose up -d
   ```

5. You can connect to the virtual display using a VNC client at `localhost:5900` (password: "secret")

## Running the Demo

Run the main script:

```bash
python autoqa.py
```

## Documentation

- [OpenAI Agents Python documentation](https://openai.github.io/openai-agents-python/)
- This project uses Docker to create a virtual Ubuntu environment with Xfce desktop
- The `execute.py` module provides a VM class that extends the Agent Computer to interact with the Docker container
