from motor.motor_asyncio import AsyncIOMotorClient
from .settings import settings
import logging
import ssl

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None

db_instance = Database()

async def connect_db():
    try:
        logger.info("Connecting to MongoDB Atlas...")
        
        db_instance.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=20000,
            retryWrites=True
        )
        
        await db_instance.client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.DATABASE_NAME}")
        
        await create_indexes()
        
    except Exception as e:
        logger.error(f" MongoDB connection failed: {str(e)}")
        raise

async def close_db():
    if db_instance.client:
        db_instance.client.close()
        logger.info("MongoDB connection closed")

def get_database():
    return db_instance.client[settings.DATABASE_NAME]

async def create_indexes():
    try:
        db = get_database()
        
        await db.employees.create_index("employee_id", unique=True)
        await db.employees.create_index("email", unique=True)
        
        await db.attendance.create_index([("employee_id", 1), ("date", -1)])
        await db.attendance.create_index("date")
        
        logger.info("Database indexes created")
    except Exception as e:
        logger.warning(f"Index creation warning: {e}")