from fastapi.templating import Jinja2Templates
from fastapi import Request
from abc import ABC, abstractmethod

templates = Jinja2Templates(directory="templates")


class Visitor(ABC):
    @abstractmethod
    def visit_article(self, article: "Article") -> None:
        pass

    @abstractmethod
    def visit_video(self, video: "Video") -> None:
        pass

    @abstractmethod
    def visit_image(self, image: "Image") -> None:
        pass


class BaseContent(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor):
        pass


class Content(BaseContent):
    def __init__(
        self,
        title: str,
        content: str,
    ) -> None:
        self.title: str = title
        self.content: str = content
        self.content_context: dict = {"title": title, "content": content}


class Article(Content):
    def __init__(
        self,
        title: str,
        content: str,
        author: str,
    ) -> None:
        super().__init__(title, content)
        self.author: str = author

    def accept(self, visitor: Visitor):
        visitor.visit_article(self)


class Video(Content):
    def __init__(
        self,
        title: str,
        content: str,
        duration: int,
    ) -> None:
        super().__init__(title, content)
        self.duration = duration

    def accept(self, visitor: Visitor):
        visitor.visit_video(self)


class Image(Content):
    def __init__(
        self,
        title: str,
        content: str,
        resolution: str,
    ) -> None:
        super().__init__(title, content)
        self.resolution = resolution

    def accept(self, visitor: Visitor):
        visitor.visit_image(self)


class ContentRenderer(Visitor):
    def visit_article(self, article: Article):
        article.content_context["author"] = article.author

    def visit_video(self, video: Video):
        video.content_context["duration"] = video.duration

    def visit_image(self, image: Image):
        image.content_context["resolution"] = image.resolution


content_renderer = ContentRenderer()


def handle_content(item: Content, request: Request):
    template_name = ""
    content_context = {"request": request}

    match item:
        case Article():
            template_name = "article.html"
            item.accept(content_renderer)
            content_context.update(item.content_context)
        case Video():
            template_name = "video.html"
            item.accept(content_renderer)
            content_context.update(item.content_context)
        case Image():
            template_name = "image.html"
            item.accept(content_renderer)
            content_context.update(item.content_context)

    return templates.TemplateResponse(
        name=template_name,
        context=content_context,
    )
