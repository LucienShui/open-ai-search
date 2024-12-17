FROM python:3.12-alpine
COPY ./requirements.txt /requirements.txt
RUN python3 -m pip install -r /requirements.txt
COPY ./ /app
WORKDIR /app
ENTRYPOINT ["uvicorn", "open_ai_search.api:app"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD wget -q -O- http://127.0.0.1:8000/api/v1/health || exit 1
EXPOSE 8000
