import json
from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates
from my_library.logger import get_logger

from api.exceptions import VersionQueryParamRequired
from utils.openapi import get_services_openapis

logger = get_logger()

CURR_DIR = Path(__file__).resolve()

templates = Jinja2Templates(directory=CURR_DIR.parent / "htmls")


async def schemas_intersection(req: Request):
    if "version" not in req.query_params:
        raise VersionQueryParamRequired(endpoint="/docs/schemas_intersection")
    version = req.query_params["version"]
    show_internal = req.query_params.get("show_internal", "").lower() == "true"
    services_openapis = await get_services_openapis(
        show_internal=show_internal, version=version
    )

    schemas_to_services = {}
    schemas_strings = {}

    for service_name, data in (openapi for openapi in services_openapis if openapi):
        for schema_name in sorted(data["components"]["schemas"]):
            schema_data = data["components"]["schemas"][schema_name]
            schema_as_str = json.dumps(schema_data, sort_keys=True)
            schemas_strings.setdefault(schema_name, set()).add(schema_as_str)
            schemas_to_services.setdefault(f"{schema_name}", []).append(service_name)
    table = {}
    for schema_name in schemas_strings:
        if len(schemas_strings[schema_name]) > 1:
            table[schema_name] = schemas_to_services[schema_name]
    return templates.TemplateResponse(
        "intersection.html",
        {
            "request": req,
            "table": table,
        },
    )
