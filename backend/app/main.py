from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, file, acl
from app.core.config import settings

app = FastAPI(
    title="Linux ACL Manager API",
    description="API for managing Linux ACLs on research storage systems",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(file.router, prefix="/api/files", tags=["File Management"])
app.include_router(acl.router, prefix="/api/acl", tags=["ACL Management"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": app.version}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)