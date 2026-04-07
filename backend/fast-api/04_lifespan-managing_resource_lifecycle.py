from re import S

from fast_api import FastAPI
from contextlib import asynccontextmanager

from jira_client import JiraClient



# we want to create a connection pool with an external API only once when the app starts
# and reuse it for all requests. 
# This is more efficient than creating a new client/ connection for each request.
# and cleanly close the connection pool when the app ends


# An async generator function that FastAPI calls once when the server starts.
# Receives the app instance.
@asynccontextmanager
async def lifecycle_manager(app: FastAPI):
    # Startup code (runs before any request is served).
    # Creates one shared connection pool to the Jira API.
    # This happens once, not per request — that's the whole point.


    # This is a mypy warning, not a runtime error.
    # mypy doesn't understand that Pydantic's BaseSettings loads values from .env at runtime.
    # It sees Settings() with no arguments and thinks you forgot to pass JIRA_EMAIL, JIRA_API_TOKEN, etc.
    # The code works fine — Pydantic reads those values from your `.env` file. 
    # This is a false positive from the type checker.
    settings = Settings()  # Load settings from .env file

    client = JiraClient(settings=settings)

    app.state.jira_client = client   # ← store it on app.state

    # This is where your app lives. After `yield`, FastAPI starts accepting requests.
    # The function pauses here for the entire lifetime of the app (could be hours, days, etc.).
    # Think of it as: everything above `yield` = startup, everything below `yield` = shutdown.
    yield # ← bare yield, nothing to pass

    # Shutdown code (runs when the server stops — e.g., Ctrl+C or deployment restart).
    # Cleanly closes the HTTP connection pool — releases sockets, avoids resource leaks.
    await client.close()


app = FastAPI(lifespan=lifecycle_manager)


# Visual timeline:

# Server starts
#   ↓
# client = JiraClient()      ← startup: open connections
#   ↓
# yield                       ← app is running, handling requests...
#   ↓
# (Ctrl+C / server stops)
#   ↓
# await client.aclose()       ← shutdown: clean up resources
#   ↓
# Server exits



