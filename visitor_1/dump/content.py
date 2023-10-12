from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")


class Content:
    def __init__(
        self,
        title: str,
        content: str,
    ) -> None:
        self.title: str = title
        self.content: str = content

    def render(self):
        pass


class Article(Content):
    def __init__(
        self,
        title: str,
        content: str,
        author: str,
    ) -> None:
        super().__init__(title, content)
        self.author: str = author

    def render(self):
        return {
            "author": self.author,
            "content": self.content,
            "title": self.title,
        }


class Video(Content):
    def __init__(
        self,
        title: str,
        content: str,
        duration: int,
    ) -> None:
        super().__init__(title, content)
        self.duration = duration

    def render(self):
        return {
            "duration": self.duration,
            "content": self.content,
            "title": self.title,
        }


class Image(Content):
    def __init__(
        self,
        title: str,
        content: str,
        resolution: str,
    ) -> None:
        super().__init__(title, content)
        self.resolution = resolution

    def render(self):
        return {
            "resolution": self.resolution,
            "content": self.content,
            "title": self.title,
        }


def handle_content(item: Content, request: Request):
    template_name = ""
    content_context = {"request": request}
    if isinstance(item, Article):
        template_name = "article.html"
        content_context = content_context | item.render()
    elif isinstance(item, Video):
        template_name = "video.html"
        content_context = content_context | item.render()
    elif isinstance(item, Image):
        template_name = "image.html"
        content_context = content_context | item.render()
    return templates.TemplateResponse(
        name=template_name,
        context=content_context,
    )
