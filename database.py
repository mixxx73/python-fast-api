import motor.motor_asyncio
from uuid import UUID
from bson.codec_options import CodecOptions, UuidRepresentation

MONGODB_URL = "mongodb://localhost:27017"
MONGODB_DB_NAME = "contacts_assets_db"
MONGODB_CONTACTS_COLLECTION = "contacts"
MONGODB_ASSETS_COLLECTION = "assets"

client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGODB_URL,
    uuidRepresentation='standard' # Important for handling UUIDs correctly
)

db = client[MONGODB_DB_NAME]

uuid_codec_options = CodecOptions(uuid_representation=UuidRepresentation.STANDARD)

contacts_collection = db.get_collection(
    MONGODB_CONTACTS_COLLECTION,
    codec_options=uuid_codec_options
)
assets_collection = db.get_collection(
    MONGODB_ASSETS_COLLECTION,
    codec_options=uuid_codec_options
)

# Optional: Function to close the connection (useful for testing or shutdown events)
async def close_mongo_connection():
    client.close()

# Optional: Function to connect (useful for startup events)
async def connect_to_mongo():
    # Motor connects lazily, but you could add a ping here if needed
    pass
