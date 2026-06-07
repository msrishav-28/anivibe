
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import init_db, close_db, engine
from sqlalchemy import text

async def drop_social_tables():
    print("Initializing database...")
    await init_db()
    
    print("Dropping social tables...")
    async with engine.begin() as conn:
        # Drop dependent table first
        await conn.execute(text("DROP TABLE IF EXISTS activities CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS friends CASCADE"))
        
    print("Tables dropped successfully.")
    await close_db()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(drop_social_tables())
