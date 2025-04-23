import motor.motor_asyncio
from uuid import UUID
from bson.codec_options import CodecOptions, UuidRepresentation
from config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.mongodb_url,
    uuidRepresentation='standard' # Important for handling UUIDs correctly
)

db = client[settings.mongodb_db_name]

uuid_codec_options = CodecOptions(uuid_representation=UuidRepresentation.STANDARD)

contacts_collection = db.get_collection(
    settings.mongodb_contacts_collection,
    codec_options=uuid_codec_options
)
assets_collection = db.get_collection(
    settings.mongodb_assets_collection,
    codec_options=uuid_codec_options
)

# Optional: Function to close the connection (useful for testing or shutdown events)
async def close_mongo_connection():
    client.close()

# Optional: Function to connect (useful for startup events)
async def connect_to_mongo():
    # Motor connects lazily, but you could add a ping here if needed
    pass
