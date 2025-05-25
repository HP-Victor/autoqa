# AutoQA GitHub Actions Workflows

This directory contains GitHub Actions workflows for running automated QA using the OpenAI Agents to control a virtual Ubuntu environment.

## Available Workflows

1. `reusable-autoqa.yml` - A reusable workflow that can be called from other workflows
2. `call-autoqa-example.yml` - An example of how to call the reusable workflow
3. `run-autoqa.yml` - A standalone workflow triggered by pushes to the main branch

## Using the Reusable Workflow

The reusable workflow pattern allows you to easily incorporate AutoQA into your own repositories without duplicating code.

### Basic Usage

Create a new workflow file in your repository (e.g., `.github/workflows/my-autoqa.yml`) with the following content:

```yaml
name: My AutoQA Workflow

on:
  workflow_dispatch:  # Allows manual triggering
  schedule:
    - cron: '0 0 * * 1'  # Run every Monday at midnight

jobs:
  run-tests:
    uses: yourusername/autoqa/.github/workflows/reusable-autoqa.yml@main
    with:
      prompt: "Open firefox and go to your-website.com"
    secrets:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Available Parameters

The reusable workflow accepts the following inputs:

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `prompt` | Instructions for the AutoQA agent | "Open firefox and go to mitchellhynes.com" | No |
| `max_turns` | Maximum conversation turns for the agent | "100" | No |
| `python_version` | Python version to use | "3.10" | No |
| `openai_model` | OpenAI model to use for the agent | "computer-use-preview" | No |

### Required Secrets

| Secret | Description | Required |
|--------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key with access to the agent models | Yes |
| `VNC_HOST` | Host for the VNC connection | No (defaults to 'localhost') |
| `VNC_PORT` | Port for the VNC connection | No (defaults to '5900') |
| `VNC_PASSWORD` | Password for the VNC connection | No (defaults to 'secret') |

## Setting Up in Your Repository

To use this workflow in your own repository:

1. Fork or clone the AutoQA repository
2. Add your `OPENAI_API_KEY` to your repository secrets
3. Create a new workflow file that calls the reusable workflow
4. Customize the parameters as needed

## Workflow Artifacts

After each run, the workflow will save:

- Screenshots taken during the agent's execution
- These artifacts are retained for 7 days

## Example Run

The example workflow (`call-autoqa-example.yml`) shows how to call the reusable workflow with custom parameters. To run it:

1. Go to the "Actions" tab in your repository
2. Select "Run AutoQA Example" from the workflows list
3. Click "Run workflow"
4. Optionally modify the default parameters
5. View the logs and artifacts after completion

## Troubleshooting

If you encounter issues with the workflow:

1. Check that your OPENAI_API_KEY has access to the computer-use-preview model
2. Ensure the Docker service is available in your GitHub Actions runner
3. Check the logs for any error messages related to VNC connection issues
4. If using custom VNC settings, verify that all VNC parameters are correctly specified

## Advanced Configuration

You can customize the workflow by:

1. Modifying the Docker container settings in `autoqa/docker/compose.yml`
2. Changing the agent's instructions in `autoqa/computer_use_agent.py`
3. Adding custom testing scripts that the agent can execute

## License

This workflow is provided under the same license as the AutoQA project.