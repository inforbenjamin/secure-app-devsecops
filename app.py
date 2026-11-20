import logging
import re

from flask import Flask, request
from markupsafe import escape
from prometheus_client import Counter
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)  # expone /metrics para Prometheus/Grafana

# Metrica de seguridad: entradas sospechosas o invalidas
SUSPICIOUS = Counter(
    "suspicious_requests_total",
    "Peticiones con entrada sospechosa o invalida",
    ["reason"],
)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("secure-app")

# Solo letras, numeros, espacios, punto, guion y guion bajo (1 a 50 caracteres)
NAME_RE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9 _.\-]{1,50}$")


@app.after_request
def add_security_headers(resp):
    resp.headers["Content-Security-Policy"] = "default-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    resp.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    return resp


@app.route("/hello")
def hello():
    name = request.args.get("name", "World")
    if not NAME_RE.fullmatch(name):
        reason = "xss_pattern" if "<" in name or ">" in name else "invalid_name"
        SUSPICIOUS.labels(reason=reason).inc()
        log.warning("Entrada rechazada ip=%s reason=%s value=%r",
                    request.remote_addr, reason, name[:80])
        return "Invalid name", 400
    return f"Hello, {escape(name)}!"


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    # Solo para desarrollo local; en Docker se usa gunicorn
    app.run(host="127.0.0.1", port=5000, debug=False)