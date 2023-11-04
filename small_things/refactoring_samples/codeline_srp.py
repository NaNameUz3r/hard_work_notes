# 1
# BEFORE
def log_overlaps_to_stdout(
    version_overlaps: dict,
):
    for service in version_overlaps["services_with_overlapping_schemas"]:
        print("=" * 80)
        print(
            f"OVERLAPS WITH SERVICE {service['service_name']} (v{version_overlaps['version'].replace('-','_')})"
        )
        print("=" * 80)

        (lambda print_list: [print(overlap) for overlap in print_list])(
            service["overlaps"]
        )

        print("\n")

    print("#" * 80 + "\n\n")


# AFTER
def log_overlaps_to_stdout(
    version_overlaps: dict,
):
    for service in version_overlaps["services_with_overlapping_schemas"]:
        print("=" * 80)
        formatted_version = f"v{version_overlaps['version'].replace('-','_')}"
        print(f"OVERLAPS WITH SERVICE {service['service_name']} ({formatted_version})")
        print("=" * 80)

        (lambda print_list: [print(overlap) for overlap in print_list])(
            service["overlaps"]
        )

        print("\n")

    print("#" * 80 + "\n\n")


#########################################################################################
# 2
# BEFORE:


def find_overlaps_in_version(
    version: str,
    openapi_json: dict,
) -> tuple[dict, bool]:
    this_service_name = get_service_name()
    if this_service_name == "":
        print("[ERROR] Can't get service name of this service", file=sys.stderr)
        raise SystemExit(1)
    version_to_check = {
        "service_name": this_service_name,
        "version": version,
        "schema_names": list(openapi_json["components"]["schemas"].keys()),
    }

    return (
        overlaps := request_overlaps_from_collector(version_to_check),
        is_any_overlaps_found(overlaps),
    )


def is_any_overlaps_found(version_overlaps: dict) -> bool:
    return len(version_overlaps["services_with_overlapping_schemas"]) > 0


def mock_init(self, app, *args, **kwargs):
    app_object = app.app
    overlaps_summary = []
    for version, openapi_json in app_object.swaggers.items():
        if not is_valid_version_string(version):
            print(f"[INFO] Skipping swagger item: {version}\n\n")
            continue
        version_overlaps, is_found = find_overlaps_in_version(version, openapi_json)
        if is_found:
            log_overlaps_to_stdout(version_overlaps)
            overlaps_summary.append(
                {
                    "version": version_overlaps["version"],
                    "total_overlapping_services": len(
                        version_overlaps["services_with_overlapping_schemas"]
                    ),
                    "total_overlaps": sum(
                        [
                            len(x["overlaps"])
                            for x in version_overlaps[
                                "services_with_overlapping_schemas"
                            ]
                        ]
                    ),
                }
            )
    log_summary_to_stdout(overlaps_summary)


# AFTER:


def find_overlaps_in_version(
    version: str,
    openapi_json: dict,
) -> dict:
    this_service_name = get_service_name()
    if this_service_name == "":
        print("[ERROR] Can't get service name of this service", file=sys.stderr)
        raise SystemExit(1)
    version_to_check = {
        "service_name": this_service_name,
        "version": version,
        "schema_names": list(openapi_json["components"]["schemas"].keys()),
    }

    return request_overlaps_from_collector(version_to_check)


def mock_init(self, app, *args, **kwargs):
    app_object = app.app
    overlaps_summary = []
    for version, openapi_json in app_object.swaggers.items():
        if not is_valid_version_string(version):
            print(f"[INFO] Skipping swagger item: {version}\n\n")
            continue
        version_overlaps = find_overlaps_in_version(version, openapi_json)
        log_overlaps_to_stdout(version_overlaps)
        overlaps_summary.append(
            {
                "version": version_overlaps["version"],
                "total_overlapping_services": len(
                    version_overlaps["services_with_overlapping_schemas"]
                ),
                "total_overlaps": sum(
                    [
                        len(x["overlaps"])
                        for x in version_overlaps["services_with_overlapping_schemas"]
                    ]
                ),
            }
        )
    log_summary_to_stdout(overlaps_summary)


#########################################################################################
# 3
# BEFORE:


def log_overlaps_to_stdout(
    version_overlaps: dict,
):
    for service in version_overlaps["services_with_overlapping_schemas"]:
        print("=" * 80)
        formatted_version = f"v{version_overlaps['version'].replace('-','_')}"
        print(f"OVERLAPS WITH SERVICE {service['service_name']} ({formatted_version})")
        print("=" * 80)

        (lambda print_list: [print(overlap) for overlap in print_list])(
            service["overlaps"]
        )

        print("\n")

    print("#" * 80 + "\n\n")


# AFTER:


def log_overlaps_to_stdout(
    version_overlaps: dict,
):
    for service in version_overlaps["services_with_overlapping_schemas"]:
        print("=" * 80)
        formatted_version = f"v{version_overlaps['version'].replace('-','_')}"
        print(f"OVERLAPS WITH SERVICE {service['service_name']} ({formatted_version})")
        print("=" * 80)

        for overlap in service["overlaps"]:
            print(overlap)

        print("\n")

    print("#" * 80 + "\n\n")


#########################################################################################
# 4
# BEFORE:


def find_overlaps_in_version(
    version: str,
    openapi_json: dict,
) -> dict:
    this_service_name = get_service_name()
    if this_service_name == "":
        print("[ERROR] Can't get service name of this service", file=sys.stderr)
        raise SystemExit(1)

    version_to_check = {
        "service_name": this_service_name,
        "version": version,
        "schema_names": list(openapi_json["components"]["schemas"].keys()),
    }

    return request_overlaps_from_collector(version_to_check)


# AFTER:


def find_overlaps_in_version(
    version: str,
    openapi_json: dict,
) -> dict:
    this_service_name = get_service_name()
    if this_service_name == "":
        print("[ERROR] Can't get service name of this service", file=sys.stderr)
        raise SystemExit(1)

    schema_names = openapi_json["components"]["schemas"].keys()
    version_payload = {
        "service_name": this_service_name,
        "version": version,
        "schema_names": list(schema_names),
    }

    return request_overlaps_from_collector(version_payload)


#########################################################################################
# 5
# BEFORE:


def request_overlaps_from_collector(version_payload: dict):
    if OPENAPI_COLLECTOR_URL is None or OPENAPI_COLLECTOR_URL == "":
        print(
            "[ERROR]: OPENAPI_COLLECTOR_URL env variable is not set, can't request overlaps",
            file=sys.stderr,
        )
        raise SystemExit(1)

    collector_response = httpx.post(
        url=OPENAPI_COLLECTOR_URL,
        json=version_payload,
        timeout=10,
    )

    try:
        collector_response.raise_for_status()
        version_overlaps = collector_response.json()
    except httpx.HTTPError as http_err:
        print(f"HTTP error occurred:\n{http_err}", file=sys.stderr)
        raise SystemExit(1) from http_err
    except json.JSONDecodeError as json_err:
        print(f"JSON decoding error occurred:\n{json_err}", file=sys.stderr)
        raise SystemExit(1) from json_err
    except Exception as exception:
        print(f"An error occurred:\n{exception}", file=sys.stderr)
        raise SystemExit(1) from exception

    return version_overlaps


# AFTER:


def request_overlaps_from_collector(version_payload: dict):
    if OPENAPI_COLLECTOR_URL is None or OPENAPI_COLLECTOR_URL == "":
        print(
            "[ERROR]: OPENAPI_COLLECTOR_URL env variable is not set, can't request overlaps",
            file=sys.stderr,
        )
        raise SystemExit(1)

    collector_response = httpx.post(
        url=OPENAPI_COLLECTOR_URL,
        json=version_payload,
        timeout=10,
    )

    try:
        collector_response.raise_for_status()
    except httpx.HTTPError as http_err:
        print(f"HTTP error occurred:\n{http_err}", file=sys.stderr)
        raise SystemExit(1) from http_err

    try:
        version_overlaps = collector_response.json()
    except json.JSONDecodeError as json_err:
        print(f"JSON decoding error occurred:\n{json_err}", file=sys.stderr)
        raise SystemExit(1) from json_err

    return version_overlaps


#########################################################################################
# 6
# BEFORE:


def mock_init(self, app, *args, **kwargs):
    app_object = app.app
    overlaps_summary = []
    for version, openapi_json in app_object.swaggers.items():
        if not is_valid_version_string(version):
            print(f"[INFO] Skipping swagger item: {version}\n\n")
            continue
        version_overlaps = find_overlaps_in_version(version, openapi_json)
        log_overlaps_to_stdout(version_overlaps)
        overlaps_summary.append(
            {
                "version": version_overlaps["version"],
                "total_overlapping_services": len(
                    version_overlaps["services_with_overlapping_schemas"]
                ),
                "total_overlaps": sum(
                    [
                        len(x["overlaps"])
                        for x in version_overlaps["services_with_overlapping_schemas"]
                    ]
                ),
            }
        )
    log_summary_to_stdout(overlaps_summary)


# AFTER:


def mock_init(self, app, *args, **kwargs):
    app_object = app.app

    is_any_overlap = False
    for swagger_item_name, openapi_json in app_object.swaggers.items():
        if not is_valid_version_string(swagger_item_name):
            # Skipping item, if it is not API version. (webhooks, etc.)
            continue

        print(f"Checking overlaps for version {swagger_item_name}...")
        version_overlaps = find_overlaps_in_version(swagger_item_name, openapi_json)
        if version_overlaps is not None:
            is_any_overlap = True
        report_version_overlaps(version_overlaps)

    report_overlaps_summary(is_any_overlap)
