import uvicorn
from fastapi import FastAPI
from src.routers.apis import router

app = FastAPI(title="GA4GH DOI Service")
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
