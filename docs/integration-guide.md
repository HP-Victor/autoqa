# AutoQA Integration Guide

This comprehensive guide explains how to integrate AutoQA's GitHub Actions workflows into your own repositories and projects. AutoQA provides powerful automated testing capabilities through OpenAI's agent technology and a virtual Ubuntu environment.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Integration Methods](#integration-methods)
   - [Method 1: Using the Reusable Workflow](#method-1-using-the-reusable-workflow)
   - [Method 2: Forking the Entire Repository](#method-2-forking-the-entire-repository)
   - [Method 3: Custom Integration](#method-3-custom-integration)
3. [Configuration Options](#configuration-options)
4. [Advanced Use Cases](#advanced-use-cases)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)

## Quick Start

For the fastest integration:

1. Create a `.github/workflows/autoqa.yml` file in your repository
2. Add the following content:

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
    secrets:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

3. Add your `OPENAI_API_KEY` to your repository secrets
4. Push the changes to trigger the workflow manually or wait for the scheduled run

## Integration Methods

### Method 1: Using the Reusable Workflow

The simplest integration method is using AutoQA's reusable workflow. This approach requires minimal setup and maintenance.

**Steps:**

1. Create a workflow file in your repository (e.g., `.github/workflows/autoqa.yml`)
2. Reference the reusable workflow from the AutoQA repository
3. Configure inputs and secrets
4. Push the changes to your repository

**Example:**

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
      python_version: "3.10"
      openai_model: "computer-use-preview"
    secrets:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

**Advantages:**
- Minimal setup
- Automatically benefits from updates to the AutoQA repository
- No need to maintain the core code

**Disadvantages:**
- Limited customization options
- Depends on the availability of the referenced repository

### Method 2: Forking the Entire Repository

For more control, fork the entire AutoQA repository and customize it for your needs.

**Steps:**

1. Fork the AutoQA repository to your GitHub account
2. Modify the workflows and scripts as needed
3. Add your repository secrets
4. Use the workflows directly from your fork

**Advantages:**
- Full control over all aspects of AutoQA
- Can make extensive modifications
- Independent from the original repository

**Disadvantages:**
- Need to manually incorporate updates from the original repository
- More complex setup
- More to maintain

### Method 3: Custom Integration

For advanced users, extract only the components you need from AutoQA and integrate them into your existing workflow.

**Steps:**

1. Copy the relevant Python scripts and Docker configurations from AutoQA
2. Create your own workflow file using these components
3. Customize as needed for your specific requirements

This method is recommended only for users with specific requirements that cannot be met by the other integration methods.

## Configuration Options

### Workflow Inputs

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

### Trigger Options

You can configure various triggers for your workflow:

```yaml
on:
  # Manual trigger with parameters
  workflow_dispatch:
    inputs:
      prompt:
        description: 'Custom prompt for the AutoQA agent'
        required: false
        type: string
        default: 'Open firefox and go to your-website.com'
  
  # Scheduled runs
  schedule:
    - cron: '0 0 * * 1'  # Run every Monday at midnight
  
  # Run on pushes to specific branches
  push:
    branches: [main, develop]
    paths:
      - 'frontend/**'
      - 'backend/**'
  
  # Run on pull requests
  pull_request:
    types: [opened, synchronize]
    branches: [main]
```

## Advanced Use Cases

### Testing Web Applications

To test a web application, use a prompt that navigates to your site and interacts with it:

```yaml
jobs:
  run-tests:
    uses: yourusername/autoqa/.github/workflows/reusable-autoqa.yml@main
    with:
      prompt: "Open firefox, navigate to https://your-app.com, click the login button, enter 'testuser' in the username field, enter 'password123' in the password field, and click the login button. Then verify that the dashboard page loads correctly."
    secrets:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Running Multiple Test Scenarios

To run multiple test scenarios, create separate jobs for each scenario:

```yaml
jobs:
  login-test:
    uses: yourusername/autoqa/.github/workflows/reusable-autoqa.yml@main
    with:
      prompt: "Test the login functionality at https://your-app.com"
    secrets:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  
  checkout-test:
    uses: yourusername/autoqa/.github/workflows/reusable-autoqa.yml@main
    with:
      prompt: "Test the checkout process at https://your-app.com"
    secrets:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Custom VNC Setup

If you need to use your own VNC server instead of the built-in Docker container:

```yaml
jobs:
  run-tests:
    uses: yourusername/autoqa/.github/workflows/reusable-autoqa.yml@main
    with:
      prompt: "Open firefox and navigate to your-website.com"
    secrets:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      VNC_HOST: ${{ secrets.CUSTOM_VNC_HOST }}
      VNC_PORT: ${{ secrets.CUSTOM_VNC_PORT }}
      VNC_PASSWORD: ${{ secrets.CUSTOM_VNC_PASSWORD }}
```

## Troubleshooting

### Common Issues and Solutions

1. **OpenAI API Key Issues**
   - Ensure your API key is correctly set in repository secrets
   - Verify the key has access to the required models (e.g., `computer-use-preview`)

2. **Docker Container Problems**
   - Check if the Docker service is available in your GitHub Actions runner
   - Look for error messages related to Docker compose or container creation

3. **VNC Connection Failures**
   - Verify that the VNC server is running and accessible
   - Check VNC host, port, and password settings
   - Look for network connectivity issues in the workflow logs

4. **Agent Not Completing Tasks**
   - Make sure your prompt is clear and specific
   - Increase the `max_turns` parameter for complex tasks
   - Break down complex tasks into smaller, more manageable steps

### Debug Tips

Add these steps to your workflow for better debugging:

```yaml
- name: Debug VNC Connection
  if: always()
  run: |
    echo "VNC_HOST: $VNC_HOST"
    echo "VNC_PORT: $VNC_PORT"
    echo "Testing VNC connection..."
    nc -zv $VNC_HOST $VNC_PORT || echo "Connection failed"

- name: List Docker Containers
  if: always()
  run: docker ps -a
```

## Best Practices

1. **Write Clear Prompts**
   - Be specific about what you want the agent to do
   - Break complex tasks into steps
   - Include verification steps to confirm success

2. **Use Meaningful Workflow Names**
   - Name workflows based on what they test
   - Use descriptive job names for each test scenario

3. **Set Appropriate Schedules**
   - Don't run tests too frequently to avoid API rate limits
   - Schedule critical tests more frequently than non-critical ones

4. **Manage Secrets Carefully**
   - Regularly rotate API keys
   - Use repository secrets, not hard-coded values
   - Limit access to who can see workflow logs containing sensitive information

5. **Review Test Results Regularly**
   - Set up notifications for failed tests
   - Download and review screenshots from the artifacts
   - Use the test results to improve your application

---

For more information, see the main [AutoQA documentation](https://github.com/yourusername/autoqa) or open an issue in the repository if you encounter problems not covered by this guide.