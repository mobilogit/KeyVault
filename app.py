from flask import Flask, render_template_string, request
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from datetime import datetime

app = Flask(__name__)

# 🔧 Konfiguracja Key Vault
VAULT_NAME = "mobilotest12"  # ← wpisz swoją nazwę Key Vault
KV_URL = f"https://mobilotest12.vault.azure.net"

# 🔐 Uwierzytelnienie przez Managed Identity (lub az login lokalnie)
credential = DefaultAzureCredential()
client = SecretClient(vault_url=KV_URL, credential=credential)

# 🧾 Szablon HTML
TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Expired Secrets</title></head>
<body>
    <h2>🔒 Sprawdź wygasłe sekrety</h2>
    <form method="POST">
        <button type="submit">Check Secret</button>
    </form>
    {% if secrets %}
        <h3>📜 Wygasłe sekrety:</h3>
        <ul>
        {% for name in secrets %}
            <li>{{ name }}</li>
        {% endfor %}
        </ul>
    {% elif secrets is not none %}
        <p>✅ Brak wygasłych sekretów</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    expired_secrets = None

    if request.method == "POST":
        expired_secrets = []
        for props in client.list_properties_of_secrets():
            if props.expires_on and props.expires_on < datetime.utcnow():
                expired_secrets.append(props.name)

    return render_template_string(TEMPLATE, secrets=expired_secrets)

if __name__ == "__main__":
    app.run(debug=True)
