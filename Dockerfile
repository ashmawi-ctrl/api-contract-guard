FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY contract_guard ./contract_guard

RUN pip install --no-cache-dir .

ENTRYPOINT ["api-contract-guard"]
