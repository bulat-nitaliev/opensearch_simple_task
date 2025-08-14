from pydantic import BaseModel
from typing import Optional
from model import ContentType

class SearchRequest(BaseModel):
    query: str
    content_type: Optional[ContentType] = None