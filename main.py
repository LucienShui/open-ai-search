import json
from contextlib import asynccontextmanager
from typing import Dict, AsyncIterable

import uvicorn
from fastapi import FastAPI, Request, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, HTMLResponse
from pydantic import BaseModel, Field
from sse_starlette import EventSourceResponse

from open_ai_search.config import config
from open_ai_search.rag import RAG
from open_ai_search.retriever import BingScraper, BingAPI, FallbackRetriever


class SearchRequest(BaseModel):
    q: str = Field(description="Search query")


rag: RAG = ...
home_html: str = ...


@asynccontextmanager
async def lifespan(_: FastAPI):
    global rag, home_html

    bing_scraper = BingScraper(config.bing_search_base_url, config.bing_search_max_result_cnt)
    bing_api = BingAPI()
    bing = FallbackRetriever([bing_scraper, bing_api])

    rag = RAG([bing])
    with open("resource/www/index.html", "r") as f:
        home_html = f.read()
    yield
    del rag, home_html


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.exception_handler(Exception)
async def exception_handler(_: Request, e: Exception) -> Response:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": f"{e.__class__.__name__}: {str(e)}",
            "status": 500
        }
    )


def stream(q: str, max_results: int) -> AsyncIterable:
    for response in rag.search(q):
        yield json.dumps(response, ensure_ascii=False, separators=(',', ':'))
    yield '[DONE]'


@app.get("/api/ai-search", response_model=Dict)
async def search(
        q: str = Query(description="Search query"),
        max_results: int = Query(description="Max search result to use", default=30)
):
    return EventSourceResponse(stream(q, max_results))


@app.get("/api/health")
async def healthcheck():
    return {"status": 200}


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=home_html, status_code=200)


def main():
    uvicorn.run('main:app', host='0.0.0.0', port=config.port, workers=config.workers)


if __name__ == '__main__':
    main()
