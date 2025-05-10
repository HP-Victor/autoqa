# AutoQA

A tool that uses OpenAI Agents to control a virtual Ubuntu environment and perform automated QA testing.

## GitHub Actions

This project includes a GitHub Actions workflow that automatically runs the AutoQA agent in a containerized environment. The workflow can be:

- Triggered manually through the GitHub Actions UI
- Scheduled to run daily at midnight UTC

### Manual Trigger Options

When manually triggering the workflow, you can customize:

- **Testing URL**: The URL to test (default: mitchellhynes.com)
- **Max Turns**: Maximum number of agent interaction turns (default: 100)
- **Prompt**: Custom instructions for the agent

### Requirements

The workflow requires the following GitHub secrets:

- `OPENAI_API_KEY`: Your OpenAI API key with access to the necessary models

### Artifacts

The workflow saves screenshots taken during the agent's execution as artifacts, which are retained for 7 days.

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

## GitHub Actions

To run this workflow in your own repository:

1. Fork this repository
2. Add your `OPENAI_API_KEY` to your repository secrets
3. Go to the "Actions" tab in your repository
4. Select the "Run AutoQA Agent" workflow
5. Click "Run workflow" and optionally customize the parameters
6. View the workflow logs and download screenshots from the artifacts section

You can also customize the schedule or other parameters by editing the `.github/workflows/run-autoqa.yml` file.
