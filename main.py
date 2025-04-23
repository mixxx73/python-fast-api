from fastapi import FastAPI
from database import connect_to_mongo, close_mongo_connection
from routers import contacts, assets

app = FastAPI(
    title="Contacts and Assets API",
    description="API for managing contacts and their financial assets.",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

app.include_router(contacts.router)
app.include_router(assets.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Contacts and Assets API"}

if __name__ == "__main__":
    import uvicorn
    # Use reload=True for development convenience
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
