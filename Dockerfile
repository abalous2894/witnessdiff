FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY fixtures ./fixtures

RUN pip install --no-cache-dir -e ".[api]"

EXPOSE 8080

CMD ["uvicorn", "witnessdiff.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
