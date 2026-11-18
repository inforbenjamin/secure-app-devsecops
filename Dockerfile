FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

FROM base AS test
RUN pip install --no-cache-dir pytest==8.3.4
COPY test_app.py .
RUN pytest -q

FROM base AS final
EXPOSE 5000
CMD ["python", "app.py"]
