from fastapi import FastAPI

from app.metadata import api_description, api_version, api_title, api_contacts, tags_metadata
from . import routers

app = FastAPI(
    title=api_title,
    version=api_version,
    description=api_description,
    contact=api_contacts,
    openapi_tags=tags_metadata
)

app.include_router(routers.router)
