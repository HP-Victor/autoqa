# AutoQA

A tool that uses OpenAI Agents to control a virtual Ubuntu environment and perform automated QA testing.

## GitHub Actions

This project includes GitHub Actions workflows that automatically run the AutoQA agent in a containerized environment:

### Standard Workflow

The standard workflow can be:
- Triggered manually through the GitHub Actions UI
- Scheduled to run daily at midnight UTC

### Reusable Workflow

The project also provides a **reusable workflow** that can be easily integrated into other repositories:

```yaml
jobs:
  run-autoqa:
    uses: yourusername/autoqa/.github/workflows/reusable-autoqa.yml@main
    with:
      prompt: "Open firefox and go to your-website.com"
    secrets:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

See `.github/workflows/README.md` for comprehensive documentation on using the reusable workflow.

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

### Using the Standard Workflow

To run the standard workflow in your own repository:

1. Fork this repository
2. Add your `OPENAI_API_KEY` to your repository secrets
3. Go to the "Actions" tab in your repository
4. Select the "Run AutoQA Agent" workflow
5. Click "Run workflow" and optionally customize the parameters
6. View the workflow logs and download screenshots from the artifacts section

You can customize the schedule or other parameters by editing the `.github/workflows/run-autoqa.yml` file.

### Using the Reusable Workflow

To integrate the reusable workflow into your existing repository:

1. Create a new workflow file in your repository (e.g., `.github/workflows/autoqa.yml`)
2. Reference the reusable workflow from this repository
3. Configure inputs and secrets as needed

Example:
```yaml
name: AutoQA Tests

on:
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * 1'  # Run every Monday at midnight

jobs:
  run-tests:
    uses: yourusername/autoqa/.github/workflows/reusable-autoqa.yml@main
    with:
      prompt: "Open firefox and navigate to your-website.com"
      max_turns: "150"
    secrets:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

For detailed instructions and advanced configuration options, see the workflow documentation in `.github/workflows/README.md`.
