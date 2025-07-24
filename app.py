from flask import Flask, render_template_string, request
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import HttpResponseError
from datetime import datetime

app = Flask(__name__)

# 🔧 Konfiguracja Key Vault
VAULT_NAME = "your-key-vault-name"  # ← wpisz tutaj nazwę swojego Key Vaulta
KV_URL = f"https://{VAULT_NAME}.vault.azure.net"

# 🔐 Uwierzytelnienie przez Managed Identity lub az login
credential = DefaultAzureCredential()
client = SecretClient(vault_url=KV_URL, credential=credential)

# 🎨 HTML Template
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Expired Secrets Viewer</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 30px; }
        h2, form { text-align: center; }
        button { padding: 10px 20px; font-size: 16px; }
        p.info { font-size: 14px; color: #333; margin-bottom: 20px; }
        .error { color: red; text-align: center; font-weight: bold; }
    </style>
</head>
<body>
    <p class="info"><strong>Connected to Key Vault:</strong> {{ vault_name }}</p>
    <h2>Check for expired secrets 🔒</h2>
    <form method="POST">
        <div style="text-align:center;">
            <button type="submit">🔍 Check Secret</button>
        </div>
    </form>
    {% if error %}
        <p class="error">🚫 {{ error }}</p>
    {% endif %}
    {% if secrets %}
        <h3>📜 Expired secrets:</h3>
        <ul>
        {% for name in secrets %}
            <li>{{ name }}</li>
        {% endfor %}
        </ul>
    {% elif secrets is not none %}
        <p style="text-align:center;">✅ No expired secrets found</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    expired_secrets = None
    error_message = None

    if request.method == "POST":
        expired_secrets = []
        try:
            for props in client.list_properties_of_secrets():
                if props.expires_on and props.expires_on < datetime.utcnow():
                    expired_secrets.append(props.name)
        except HttpResponseError as e:
            if e.status_code == 403:
                error_message = "Access denied: Your identity does not have permission to list secrets in this Key Vault."
            else:
                error_message = f"Unexpected error: {e.message}"

    return render_template_string(
        TEMPLATE,
        secrets=expired_secrets,
        vault_name=VAULT_NAME,
        error=error_message
    )

if __name__ == "__main__":
    app.run(debug=True)
