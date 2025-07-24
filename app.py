from flask import Flask, render_template_string, request
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import HttpResponseError
from datetime import timezone

app = Flask(__name__)

# 🔧 Wpisz nazwę swojego Key Vault
VAULT_NAME = "mobilotest12"
KV_URL = f"https://mobilotest12.vault.azure.net"

# 🔐 Autoryzacja przez Managed Identity
credential = DefaultAzureCredential()
client = SecretClient(vault_url=KV_URL, credential=credential)

# 🎨 HTML Template
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>All Secrets Viewer</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 40px; }
        h2, form, p.info { text-align: center; }
        button { padding: 10px 20px; font-size: 16px; }
        .error { color: red; text-align: center; font-weight: bold; margin-top: 20px; }
        ul { font-size: 16px; }
    </style>
</head>
<body>
    <p class="info"><strong>Connected to Key Vault:</strong> {{ vault_name }}</p>
    <h2>Check all secrets 🔒</h2>
    <form method="POST">
        <div style="text-align:center;">
            <button type="submit">🔍 Check Secret</button>
        </div>
    </form>
    {% if error %}
        <p class="error">🚫 {{ error }}</p>
    {% endif %}
    {% if secrets %}
        <h3>📜 All secrets:</h3>
        <ul>
        {% for name in secrets %}
            <li>{{ name }}</li>
        {% endfor %}
        </ul>
    {% elif secrets is not none %}
        <p style="text-align:center;">✅ No secrets found</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    all_secrets = None
    error_message = None

    if request.method == "POST":
        all_secrets = []
        try:
            for props in client.list_properties_of_secrets():
                all_secrets.append(props.name)
        except HttpResponseError as e:
            if e.status_code == 403:
                error_message = (
                    "Access denied: Your Managed Identity lacks permission to list secrets. "
                    "Try assigning the 'Key Vault Reader' role."
                )
            else:
                error_message = f"Unexpected error: {e.message or str(e)}"
        except Exception as e:
            error_message = f"Unhandled exception: {str(e)}"

    return render_template_string(
        TEMPLATE,
        secrets=all_secrets,
        vault_name=VAULT_NAME,
        error=error_message
    )

if __name__ == "__main__":
    app.run(debug=True)
