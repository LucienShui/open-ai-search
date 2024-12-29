# Open AI Search

> This project is still under development.

Open AI Search, inspired by perplexity and metaso.

## Usage

> If you don't have poetry, install & configure it first.

```shell
pip install poetry
poetry config virtualenvs.create false
```

```shell
cp config.example.yaml config.yaml
poetry install --only main --no-root --no-directory  
uvicorn open_ai_search.api:app
```

Then open `http://localhost:8000` by default.

## Video

+ [Bilibili](https://www.bilibili.com/video/BV1zs421M7ce/)
+ [Youtube](https://youtu.be/Jp2qUYLb3K0)
