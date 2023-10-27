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


async def get_schemas_intersection(request: Request):
    version = get_api_version_param(request)
    is_show_internal = get_show_internal_param(request)

    services_openapis = await get_services_openapis(
        show_internal=is_show_internal,
        version=version,
    )

    map_of_schemas_to_services, schemas_definitions = extract_schemas_data(
        services_openapis
    )

    intersections = filter_intersections(
        map_of_schemas_to_services=map_of_schemas_to_services,
        schemas_definitions=schemas_definitions,
    )

    return templates.TemplateResponse(
        "intersection.html",
        {
            "request": request,
            "table": intersections,
        },
    )


def get_api_version_param(req: Request) -> str:
    if "version" not in req.query_params:
        raise VersionQueryParamRequired(endpoint="/docs/schemas_intersection")
    return req.query_params["version"]


def get_show_internal_param(req: Request) -> bool:
    return req.query_params.get("show_internal", "").lower() == "true"


def extract_schemas_data(openapi_specs: list):
    map_of_schemas_to_services = {}
    schemas_definitions = {}

    for service_name, data in (openapi for openapi in openapi_specs if openapi):
        for schema_name in sorted(data["components"]["schemas"]):
            schema_data = data["components"]["schemas"][schema_name]
            schema_as_str = json.dumps(schema_data, sort_keys=True)
            schemas_definitions.setdefault(schema_name, set()).add(schema_as_str)
            map_of_schemas_to_services.setdefault(f"{schema_name}", []).append(
                service_name
            )

    return (map_of_schemas_to_services, schemas_definitions)


def filter_intersections(
    map_of_schemas_to_services: dict,
    schemas_definitions: dict,
):
    schemas_intersection = {}
    for schema_name in schemas_definitions:
        if len(schemas_definitions[schema_name]) > 1:
            schemas_intersection[schema_name] = map_of_schemas_to_services[schema_name]
    return schemas_intersection
