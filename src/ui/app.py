from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.ui.pages_config import NAV_TABS, TABLE_PAGES

TEMPLATES_DIR = Path(__file__).parent / "templates"
ASSETS_DIR = Path(__file__).parent / "assets"

router = APIRouter()
assets_files = StaticFiles(directory=ASSETS_DIR)
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def render(request: Request, template_name: str, active_tab: str, **extra):
    context = {"nav_tabs": NAV_TABS, "active_tab": active_tab, **extra}
    return templates.TemplateResponse(request, template_name, context)


@router.get("/")
def home(request: Request):
    return render(request, "home.html", active_tab="/")


@router.get("/pages/register.html")
def register_page(request: Request):
    return render(request, "register.html", active_tab="/pages/register.html")


def _make_table_page_route(slug: str, config: dict):
    def handler(request: Request):
        return render(request, "table_page.html", active_tab=f"/pages/{slug}", **config)

    return handler


for _slug, _config in TABLE_PAGES.items():
    router.add_api_route(f"/pages/{_slug}", _make_table_page_route(_slug, _config), methods=["GET"])
