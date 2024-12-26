import json
import os.path
from contextlib import asynccontextmanager
from typing import Dict, AsyncIterable, Annotated, Optional

from fastapi import FastAPI, Request, status, Query, APIRouter, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, HTMLResponse
from pydantic import BaseModel, Field
from sse_starlette import EventSourceResponse

from open_ai_search.common import project_root
from open_ai_search.common.config_loader import load_config
from open_ai_search.common.trace_info import TraceInfo
from open_ai_search.config import Config
from open_ai_search.rag import RAG
from open_ai_search.retriever.ddg import DuckDuckGo


class SearchRequest(BaseModel):
    q: str = Field(description="Search query")


rag: RAG = ...
home_html: str = ...


@asynccontextmanager
async def lifespan(_: FastAPI):
    global rag, home_html
    config_path: Optional[str] = "config.yaml"
    if not os.path.isfile(config_path):
        config_path = None
    config: Config = load_config(Config, env_prefix="OAS", config_path=config_path)

    rag = RAG([DuckDuckGo(max_results=config.search.max_results)], config)
    with project_root.open("resource/www/index.html", "r") as f:
        home_html = f.read()
    yield
    del rag, home_html


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

api_v1 = APIRouter(prefix="/api/v1")


def get_trace_info(trace_id: Annotated[str | None, Header()] = None) -> TraceInfo:
    return TraceInfo(trace_id=trace_id)


@app.exception_handler(Exception)
async def exception_handler(_: Request, e: Exception) -> Response:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": f"{e.__class__.__name__}: {str(e)}",
            "status": 500
        }
    )


async def stream(q: str, max_results: int, trace_info: TraceInfo) -> AsyncIterable:
    async for response in rag.search(q, max_results, trace_info):
        yield json.dumps(response, ensure_ascii=False, separators=(',', ':'))
    yield '[DONE]'


@api_v1.get("/search", response_model=Dict)
async def search(
        q: str = Query(description="Search query"),
        max_results: int = Query(description="Max search result to use", default=None),
        trace_info: TraceInfo = Depends(get_trace_info),
):
    trace_info.info({"query": q})
    return EventSourceResponse(stream(q, max_results, trace_info))


@api_v1.get("/health")
async def healthcheck():
    return {"status": 200}


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=home_html, status_code=200)


app.include_router(api_v1)
