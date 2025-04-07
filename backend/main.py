from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, minecraft

app = FastAPI(title="Minecraft AFK Service")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(minecraft.router)

@app.get("/")
async def root():
    return {"message": "Minecraft AFK Service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
