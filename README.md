# Key Vault Flask App

A small Flask app that uses Azure Managed Identity to connect to Key Vault and display expired secrets.

## Features
- Auth via Azure Default Credential
- Lists only expired secrets
- Managed Identity & Access Policy integration

## Setup
1. Assign system managed identity to your App Service
2. Grant `list` and `get` permissions in Key Vault Access Policy
3. Deploy app using Azure or locally with Flask

## Run locally
```bash
pip install -r requirements.txt
python app.py
