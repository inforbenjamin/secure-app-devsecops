FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

FROM base AS test
RUN pip install --no-cache-dir pytest==8.3.4
COPY test_app.py .
RUN pytest -q

FROM base AS final
# Usuario sin privilegios (no root)
RUN useradd --system --no-create-home appuser
USER appuser
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "app:app"]
