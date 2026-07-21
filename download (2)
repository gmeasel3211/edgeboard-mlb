"""One-shot production refresh used by the cloud cron service."""

import asyncio
import json

from .db import SessionLocal, init_db
from .services.pipeline import Pipeline


async def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        result = await Pipeline().refresh(db)
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
