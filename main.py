import uvicorn

import load_env
from src.app import create_app
from src.graphql.core.config import settings


application = create_app()

if __name__ == "__main__":
    print("Starting server...")
    uvicorn.run("main:application", host=settings.HOST_URL, port=settings.HOST_PORT, reload=True)