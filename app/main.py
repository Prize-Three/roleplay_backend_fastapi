
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import server, resultreport


app = FastAPI()


app.include_router(server.router, prefix="/server")
app.include_router(resultreport.router, prefix="/report")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
