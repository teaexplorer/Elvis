from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import router
from db.database import engine, Base


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Achievements API", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "Achievements API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}