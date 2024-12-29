FROM python:3.12-alpine
WORKDIR /app
RUN python3 -m pip install --no-cache-dir poetry && poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-interaction --no-root --no-directory --only main
COPY ./ /app
EXPOSE 8000
ENTRYPOINT ["uvicorn", "open_ai_search.api:app", "--host", "0.0.0.0", "--port", "8000"]
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD wget -q -O- http://127.0.0.1:8000/api/v1/health || exit 1
