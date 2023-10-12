from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Sequence
from content import Content, Article, Video, Image, handle_content

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# TODO: Someone should probably store it in the databases.
articles = [
    Article(
        title="Article 1: Why you should use type-hints",
        content="Because they're cool",
        author="Admin",
    ),
    Article(
        title="Article 2: which OS system is better?",
        content="Of course one from good looking, but emotional Finnish guy",
        author="Linus",
    ),
]

videos = [
    Video(
        title="Rolling",
        content="https://www.youtube.com/embed/dQw4w9WgXcQ?si=EFZZJI5Vq9eDRpky",
        duration=10,
    ),
    Video(
        title="Cook Meal",
        content="https://www.youtube.com/embed/mhDJNfV7hjk?si=k8IhctJThd413Gqv",
        duration=20,
    ),
]

images = [
    Image(
        title="Image with kitty",
        content="/static/kitty.jpg",
        resolution="1600x1200",
    ),
    Image(
        title="Image with doggo",
        content="/static/doggo.webp>",
        resolution="605x396",
    ),
]

all_content: Sequence[Content] = articles + videos + images


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Home",
            "content": "Welcome to the awesome content site!",
        },
    )


@app.get("/content/{content_id}", response_class=HTMLResponse)
async def read_content(content_id: int, request: Request):
    if 0 <= content_id < len(all_content):
        item = all_content[content_id]
        return handle_content(item, request)
    else:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "title": "Error", "content": "Content not found"},
        )
