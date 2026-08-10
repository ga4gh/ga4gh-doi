import uvicorn
from fastapi import FastAPI
from src.routers.apis import router
from src.ui.app import router as ui_router, assets_files

app = FastAPI(title="GA4GH DOI Service")
app.include_router(router)
app.include_router(ui_router)
app.mount("/assets", assets_files, name="assets")

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
