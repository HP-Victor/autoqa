# AutoQA Standalone Integration Example

This repository demonstrates how to integrate the [AutoQA](https://github.com/yourusername/autoqa) reusable GitHub Actions workflow into your own project.

## Overview

AutoQA lets you run automated QA tests using OpenAI's agent technology to interact with a virtual Ubuntu environment through a VNC connection. This example shows the minimal setup needed to run AutoQA tests in your own repositories.

## Setup Steps

1. **Add the GitHub Actions workflow**
   - The `.github/workflows/autoqa.yml` file references the reusable workflow from the AutoQA repository
   - You can trigger this workflow manually or on a schedule

2. **Add required secrets**
   - Add your `OPENAI_API_KEY` to your repository secrets
   - This key must have access to the necessary OpenAI models (e.g., `computer-use-preview`)

3. **Customize the workflow (optional)**
   - Modify the prompt to specify what you want the agent to test
   - Adjust the schedule to run tests at your preferred time
   - Configure additional VNC parameters if needed

## Usage

### Manual Trigger

1. Go to the "Actions" tab in your repository
2. Select "AutoQA Integration Example" workflow
3. Click "Run workflow"
4. Optionally customize the prompt and max turns parameters
5. Click "Run workflow" again to start the job

### Scheduled Runs

By default, this example is configured to run weekly on Mondays at 8am UTC. You can modify the cron schedule in the workflow file.

## Results

After each workflow run, you can:

1. Review the logs to see the agent's actions and output
2. Download screenshots as artifacts to visualize what the agent saw
3. Identify any issues or bugs that were discovered

## Advanced Configuration

To customize the integration further:

1. Fork the AutoQA repository to make extensive modifications
2. Create your own test scenarios by adjusting the prompts
3. Set up multiple workflows for different testing purposes

## Troubleshooting

If you encounter issues:

1. Verify your `OPENAI_API_KEY` has the correct permissions
2. Check if the AutoQA repository has been updated
3. Consult the full documentation in the main AutoQA repository

## License

This example follows the same license as the main AutoQA project.