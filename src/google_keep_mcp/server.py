from __future__ import annotations
import json
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

import gkeepapi
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .config import Settings
from .tools import notes, lists, search, labels

load_dotenv()

logger = logging.getLogger(__name__)

_keep: gkeepapi.Keep | None = None


def get_keep() -> gkeepapi.Keep:
    """Return the authenticated Keep client, raising if not yet initialized."""
    if _keep is None:
        raise RuntimeError("Keep client not initialized. Server may not have started correctly.")
    return _keep


@asynccontextmanager
async def lifespan(app: FastMCP) -> AsyncIterator[None]:
    """Authenticate and sync Keep on startup; persist cache on shutdown."""
    global _keep
    settings = Settings()

    logging.basicConfig(level=getattr(logging, settings.log_level))
    logger.info("Authenticating with Google Keep...")

    keep_client = gkeepapi.Keep()

    try:
        if settings.cache_file and os.path.exists(settings.cache_file):
            with open(settings.cache_file) as f:
                state = json.load(f)
            keep_client.authenticate(
                settings.google_email,
                settings.google_master_token,
                state=state,
            )
            logger.info("Restored from cache, syncing incremental changes...")
        else:
            keep_client.authenticate(
                settings.google_email,
                settings.google_master_token,
            )

        _keep = keep_client
        logger.info("Authentication successful. Keep client ready.")
        yield

    except gkeepapi.exception.LoginException as e:
        logger.error("Authentication failed: %s", e)
        raise
    finally:
        if _keep is not None and settings.cache_file:
            os.makedirs(os.path.dirname(os.path.abspath(settings.cache_file)), exist_ok=True)
            state = _keep.dump()
            with open(settings.cache_file, "w") as f:
                json.dump(state, f)
            logger.info("State persisted to %s", settings.cache_file)
        _keep = None


mcp = FastMCP(
    name="google-keep-mcp",
    instructions=(
        "A server for reading and writing Google Keep notes. "
        "Always call sync after mutations (create, update, delete) to persist changes. "
        "Note IDs are stable local IDs; server_id is the Google-assigned ID."
    ),
    lifespan=lifespan,
)

notes.register(mcp)
lists.register(mcp)
search.register(mcp)
labels.register(mcp)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
