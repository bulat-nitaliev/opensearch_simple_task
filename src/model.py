from enum import Enum
from pydantic import BaseModel

class ContentType(str, Enum):
    ARTICLE = "article"
    NEWS = "news"
    TUTORIAL = "tutorial"
    REPORT = "report"

class Document(BaseModel):
    title: str
    content: str
    content_type: ContentType

class SearchResult(BaseModel):
    title: str
    snippet: str