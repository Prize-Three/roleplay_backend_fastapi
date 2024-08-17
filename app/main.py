import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mysql.models import *
import mysql.models as models
from mysql.database import *
# from mysql.database import async_engine, AsyncSessionLocal
from api import server, resultreport, voicelist, dialog


# models.Base.metadata.create_all(bind=engine)
# models.Base.metadata.create_all(bind=async_engine.sync_engine)

app = FastAPI()

# CORS 설정
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000/docs",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(server.router, prefix="/server")
app.include_router(resultreport.router, prefix="/report")
app.include_router(voicelist.router, prefix="/voice")
app.include_router(dialog.router, prefix="/dialog")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
