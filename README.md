# User Guide

1. Clone repository, create a virtual environment and install requirements with `pip install -r requirements.txt`.

2. Configure settings in .env file or your environment.

3. Login with Az CLI

4. Run `python3.12 -m discovery.cli extract` to retrieve Azure Resources properties
   - You can precise a target path to save snapshots with `python3.12 -m discovery.cli extract --target-path ./.data/`

5. Run `python3.12 -m discovery.cli run --query "List storages with allowed public access"` to get response from AI

# Architecture

## Resources Information extraction from Azure

There are two approaches to extract all resources from Azure at Control Plane level:

- Call ARM API directly
- Call Azure Resources Graph API

Current implementation uses Azure Resources Graph.

# Disclaimer

`discovery` will extract all available resources information from infrastructure resources and depends on request could send it to third-party services (AI models deployed in inference mode). Often, tag and labels information can contain PII data like employees emails.

smolagents is used as the agentic AI framework. smolagents generates code for each step. With limited chance it can generate and interpret the code which can send you data elsewhere.

Use this tool carefully and limit its scope.
