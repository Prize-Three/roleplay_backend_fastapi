
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import api.server as server, api.resultreport as resultreport

import database.models
from database.database import engine
database.models.Base.metadata.create_all(bind=engine)


app = FastAPI()

# CORS 설정
origins = [
    "http://localhost",         # 개발 중인 클라이언트 주소
    "http://localhost:3000",    # React 개발 서버 주소
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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
