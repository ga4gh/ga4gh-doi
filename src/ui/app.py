from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = Path(__file__).parent / "templates"
ASSETS_DIR = Path(__file__).parent / "assets"

router = APIRouter()
assets_files = StaticFiles(directory=ASSETS_DIR)
templates = Jinja2Templates(directory=TEMPLATES_DIR)

NAV_TABS = [
    {"label": "Home", "href": "/"},
    {"label": "Register", "href": "/pages/register.html"},
    {"label": "Standards", "href": "/pages/standards.html"},
    {"label": "Conference", "href": "/pages/conference.html"},
    {"label": "Articles", "href": "/pages/articles.html"},
    {"label": "Grants", "href": "/pages/grants.html"},
    {"label": "Posted Content", "href": "/pages/posted-content.html"},
    {"label": "Reports", "href": "/pages/reports.html"},
]

# Column lists match the SQLAlchemy models in src/models/doi.py.
TABLE_PAGES = {
    "standards.html": {
        "heading": "Standards",
        "model_name": "Standard",
        "api_endpoint": "/standards",
        "columns": [
            {"field": "id", "label": "ID"},
            {"field": "doi", "label": "DOI"},
            {"field": "title", "label": "Title"},
            {"field": "resource_url", "label": "Resource URL"},
            {"field": "resource_link", "label": "Resource Link"},
            {"field": "published_date", "label": "Published Date"},
            {"field": "item_number", "label": "Item Number"},
            {"field": "publisher_place", "label": "Publisher Place"},
            {"field": "std_designator", "label": "Standard Designator"},
            {"field": "standards_body_acronym", "label": "Standards Body Acronym"},
            {"field": "depositor_name", "label": "Depositor Name"},
            {"field": "registrant", "label": "Registrant"},
            {"field": "publisher_name", "label": "Publisher Name"},
            {"field": "standards_body_name", "label": "Standards Body Name"},
            {"field": "organization", "label": "Organization"},
            {"field": "email_address", "label": "Email Address"},
            {"field": "batch_id", "label": "Batch ID"},
            {"field": "submitted_at", "label": "Submitted At"},
            {"field": "created_by", "label": "Created By"},
            {"field": "created_at", "label": "Created At"},
            {"field": "updated_by", "label": "Updated By"},
            {"field": "updated_at", "label": "Updated At"},
            {"field": "version", "label": "Version"},
        ],
    },
    "conference.html": {
        "heading": "Conference",
        "model_name": "Conference",
        "api_endpoint": "/conference",
        "columns": [
            {"field": "id", "label": "ID"},
            {"field": "doi", "label": "DOI"},
            {"field": "resource_url", "label": "Resource URL"},
            {"field": "given_name", "label": "Given Name"},
            {"field": "surname", "label": "Surname"},
            {"field": "conference_name", "label": "Conference Name"},
            {"field": "conference_theme", "label": "Conference Theme"},
            {"field": "conference_acronym", "label": "Conference Acronym"},
            {"field": "conference_sponsor", "label": "Conference Sponsor"},
            {"field": "conference_number", "label": "Conference Number"},
            {"field": "conference_location", "label": "Conference Location"},
            {"field": "conference_start_date", "label": "Conference Start Date"},
            {"field": "conference_end_date", "label": "Conference End Date"},
            {"field": "proceedings_title", "label": "Proceedings Title"},
            {"field": "proceedings_subject", "label": "Proceedings Subject"},
            {"field": "publisher_name", "label": "Publisher Name"},
            {"field": "publisher_place", "label": "Publisher Place"},
            {"field": "publication_year", "label": "Publication Year"},
            {"field": "isbn", "label": "ISBN"},
            {"field": "timestamp", "label": "Timestamp"},
            {"field": "resource", "label": "Resource"},
            {"field": "batch_id", "label": "Batch ID"},
        ],
    },
    "articles.html": {
        "heading": "Articles",
        "model_name": "Article",
        "api_endpoint": "/articles",
        "columns": [
            {"field": "id", "label": "ID"},
            {"field": "doi", "label": "DOI"},
            {"field": "full_title", "label": "Full Title"},
            {"field": "abbrev_title", "label": "Abbreviated Title"},
            {"field": "issn", "label": "ISSN"},
            {"field": "coden", "label": "CODEN"},
            {"field": "publication_date", "label": "Publication Date"},
            {"field": "journal_volume", "label": "Journal Volume"},
            {"field": "journal_issue", "label": "Journal Issue"},
            {"field": "article_title", "label": "Article Title"},
            {"field": "contributors", "label": "Contributors"},
            {"field": "pages", "label": "Pages"},
            {"field": "resource", "label": "Resource"},
            {"field": "batch_id", "label": "Batch ID"},
        ],
    },
    "grants.html": {
        "heading": "Grants",
        "model_name": "Grant",
        "api_endpoint": "/grants",
        "columns": [
            {"field": "id", "label": "ID"},
            {"field": "doi", "label": "DOI"},
            {"field": "project_title", "label": "Project Title"},
            {"field": "recipients", "label": "Recipients"},
            {"field": "description", "label": "Description"},
            {"field": "statement", "label": "Statement"},
            {"field": "identifier", "label": "Identifier"},
            {"field": "award_amount", "label": "Award Amount"},
            {"field": "award_number", "label": "Award Number"},
            {"field": "funding_amount", "label": "Funding Amount"},
            {"field": "funder_name", "label": "Funder Name"},
            {"field": "funder_id", "label": "Funder ID"},
            {"field": "funding_scheme", "label": "Funding Scheme"},
            {"field": "start_date", "label": "Start Date"},
            {"field": "end_date", "label": "End Date"},
            {"field": "resource", "label": "Resource"},
            {"field": "batch_id", "label": "Batch ID"},
        ],
    },
    "posted-content.html": {
        "heading": "Posted Content",
        "model_name": "PostedContent",
        "api_endpoint": "/posted-content",
        "columns": [
            {"field": "id", "label": "ID"},
            {"field": "doi", "label": "DOI"},
            {"field": "group_title", "label": "Group Title"},
            {"field": "contributors", "label": "Contributors"},
            {"field": "title", "label": "Title"},
            {"field": "posted_date", "label": "Posted Date"},
            {"field": "acceptance_date", "label": "Acceptance Date"},
            {"field": "institution", "label": "Institution"},
            {"field": "funders", "label": "Funders"},
            {"field": "program", "label": "Program"},
            {"field": "resource", "label": "Resource"},
            {"field": "citations", "label": "Citations"},
            {"field": "batch_id", "label": "Batch ID"},
        ],
    },
    "reports.html": {
        "heading": "Reports",
        "model_name": "ReportWorkingPaper",
        "api_endpoint": "/reports",
        "columns": [
            {"field": "id", "label": "ID"},
            {"field": "doi", "label": "DOI"},
            {"field": "contributors", "label": "Contributors"},
            {"field": "title", "label": "Title"},
            {"field": "edition_number", "label": "Edition Number"},
            {"field": "publication_date", "label": "Publication Date"},
            {"field": "publisher_name", "label": "Publisher Name"},
            {"field": "publisher_place", "label": "Publisher Place"},
            {"field": "institution", "label": "Institution"},
            {"field": "report_number", "label": "Report Number"},
            {"field": "contract_number", "label": "Contract Number"},
            {"field": "resource", "label": "Resource"},
            {"field": "batch_id", "label": "Batch ID"},
        ],
    },
}


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
        return render(
            request,
            "table_page.html",
            active_tab=f"/pages/{slug}",
            heading=config["heading"],
            model_name=config["model_name"],
            api_endpoint=config["api_endpoint"],
            columns=config["columns"],
        )

    return handler


for _slug, _config in TABLE_PAGES.items():
    router.add_api_route(f"/pages/{_slug}", _make_table_page_route(_slug, _config), methods=["GET"])
