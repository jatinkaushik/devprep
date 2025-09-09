from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.question_controller_unified import router as question_router
from app.controllers.auth_router import router as auth_router
from app.controllers.company_router import router as company_router

app = FastAPI(title="DevPrep API - Unified", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(question_router)
app.include_router(auth_router)
app.include_router(company_router)

@app.get("/")
async def root():
    return {"message": "DevPrep API v2.0 - Unified Questions System"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
