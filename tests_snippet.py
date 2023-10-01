import base64
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import orjson
import pytest
from custom_common.serializers import convertor
from custom_db.pagination.token import b64_decode_url_params
from custom_rabbitmq import AsyncRabbitmq, Message
from httpx import AsyncClient
from httpx import Response
from package.log_trail.v2023_04_12.connectors import LogTrailAPI
from package.log_trail.v2023_04_12.pagination import PaginationFilters
from workers.log_trail_to_click.schemas import RmqLogPayload
from workers.log_trail_to_click.worker import LogsSaver

from settings.config import settings

URL = "/v1/log_trail"


def random_uuid_str() -> str:
    return str(uuid4())


@pytest.mark.parametrize("extra_headers", [{}, {"x-custom-version": "2011-11-13"}])
async def test__get_log_trail(
    log_trail_api: LogTrailAPI,
    external_id: UUID,
    internal_id: UUID,
    extra_headers: dict[str, Any],
    default_pagination_filters: PaginationFilters,
):
    msg = Message(
        body=orjson.dumps(
            {
                "timestamp": datetime(year=2022, month=1, day=1),
                "internal_id": internal_id,
                "external_id": external_id,
                "type": "request",
                "target_service": "some_service",
                "content_type": "application/json",
                "status_code": 200,
                "headers": {"Content-Type": "application/json", **extra_headers},
                "body": {"test": "test"},
                "path": "/test",
                "method": "GET",
                "params": "type=1",
            },
        ),
        headers={
            "x-row-id": random_uuid_str(),
            "x-request-id": random_uuid_str(),
        },
    )
    async_connection_class = AsyncRabbitmq(**settings.rmq_conn())
    worker = LogsSaver(async_connection_class=async_connection_class)
    await worker.on_message(msg)

    r = await log_trail_api.get_all(
        external_id=external_id,
        pagination_filters=default_pagination_filters,
    )
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1
    assert r.json()["data"][0]["method"] == "GET"
    assert r.json()["data"][0]["params"] == "type=1"
    assert r.json()["data"][0]["path"] == "/test"
    assert r.json()["data"][0]["body"] == {"test": "test"}
    log_id = r.json()["data"][0]["id"]
    r = await log_trail_api.get_log_by_id(log_id=log_id, external_id=external_id)
    assert r.status_code == 200


async def test__save_log__no_headers(
    log_trail_api: LogTrailAPI,
    internal_id: UUID,
    external_id: UUID,
):
    msg = Message(
        body=orjson.dumps(
            {
                "timestamp": datetime(2022, 1, 1),
                "internal_id": internal_id,
                "external_id": external_id,
                "type": "request",
                "target_service": "some_service",
                "content_type": "application/json",
                "status_code": 200,
            },
        ),
        headers={
            "x-row-id": random_uuid_str(),
            "x-request-id": random_uuid_str(),
        },
    )
    async_connection_class = AsyncRabbitmq(**settings.rmq_conn())
    worker = LogsSaver(async_connection_class=async_connection_class)
    await worker.on_message(msg)

    r = await log_trail_api.client.get(URL)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1
    assert r.json()["data"][0]["headers"] == {}


async def test__get_wrong_log_id(
    log_trail_api: LogTrailAPI,
    external_id: UUID,
):
    r = await log_trail_api.get_log_by_id(
        log_id=uuid4(),
        external_id=external_id,
    )
    assert r.status_code == 404


async def test__get_wrong_log_id__no_external_ud(
    log_trail_api: LogTrailAPI,
):
    r = await log_trail_api.get_log_by_id(
        log_id=uuid4(),
        external_id=None,
    )
    assert r.status_code == 404


async def test__save_log__nullable_fields(
    log_trail_api: LogTrailAPI,
    internal_id: UUID,
):
    msg = Message(
        body=orjson.dumps(
            {
                "timestamp": datetime(2022, 1, 1),
                "internal_id": internal_id,
                "external_id": None,
                "type": "request",
                "target_service": "some_service",
                "content_type": "application/json",
                "status_code": None,
                "body": None,
                "headers": None,
                "path": None,
                "method": None,
                "params": None,
                "external_user_id": None,
            },
        ),
        headers={
            "x-row-id": random_uuid_str(),
            "x-request-id": random_uuid_str(),
        },
    )
    async_connection_class = AsyncRabbitmq(**settings.rmq_conn())
    worker = LogsSaver(async_connection_class=async_connection_class)
    await worker.on_message(msg)

    r = await log_trail_api.client.get(URL)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1
    assert r.json()["data"][0]["headers"] == {}


@pytest.mark.parametrize("release_version", [None, "2011-11-13", ["2011-11-14", "2011-11-14"]])
async def test__prepare_log_to_clickhouse(
    internal_id: UUID,
    release_version: str | None,
):
    message = Message(
        body=orjson.dumps(
            {
                "timestamp": datetime(2022, 1, 1),
                "internal_id": internal_id,
                "external_id": None,
                "type": "request",
                "target_service": "some_service",
                "content_type": "application/json",
                "status_code": None,
                "body": None,
                "headers": {"x-custom-version": release_version} if release_version else None,
                "path": None,
                "method": None,
                "params": None,
                "external_user_id": None,
            },
        ),
        headers={
            "x-row-id": random_uuid_str(),
            "x-request-id": random_uuid_str(),
        },
    )
    payload = RmqLogPayload(
        **message.body_as_dict,
        databus_row_id=message.headers["x-row-id"],
        request_id=message.headers["x-request-id"],
    )
    clickhouse_payload = payload.to_clickhouse()
    release_version = release_version or ""
    assert clickhouse_payload["release_version"] == str(release_version)


async def test__get_log_trail__should_return_valid_pagination_tokens(
    client: AsyncClient,
    internal_id: UUID,
    external_id: UUID,
):
    for i in range(30):
        msg = Message(
            body=orjson.dumps(
                {
                    "timestamp": datetime(year=2022, month=1, day=1 + i),
                    "internal_id": internal_id,
                    "external_id": external_id,
                    "type": "request",
                    "body": {"This page number is": i},
                    "target_service": "some_service",
                    "content_type": "application/json",
                    "status_code": 200,
                },
            ),
            headers={
                "x-row-id": random_uuid_str(),
                "x-request-id": random_uuid_str(),
            },
        )
        async_connection_class = AsyncRabbitmq(**settings.rmq_conn())
        worker = LogsSaver(async_connection_class=async_connection_class)
        await worker.on_message(msg)

    initial_response = await client.get(
        url=URL,
        params={"page_size": 10, "type": "request"},
    )
    assert initial_response.status_code == 200
    assert len(initial_response.json()["data"]) == 10

    assert initial_response.json()["data"][0]["body"] == {"This page number is": 29}
    assert initial_response.json()["total_pages"] == 3
    assert initial_response.json()["total_logs"] == 30
    assert initial_response.json()["prev_pagination_token"] is None
    assert initial_response.json()["next_pagination_token"] is not None

    token = initial_response.json()["next_pagination_token"]

    with_token_response = await client.get(
        url=URL,
        params={"pagination_token": token},
    )
    assert with_token_response.status_code == 200
    assert len(with_token_response.json()["data"]) == 10
    assert with_token_response.json()["total_pages"] == 3
    assert with_token_response.json()["total_logs"] == 30
    assert with_token_response.json()["prev_pagination_token"] is not None
    assert with_token_response.json()["next_pagination_token"] is not None

    assert b64_decode_url_params(with_token_response.json()["prev_pagination_token"]) == {
        "type": "request",
        "page_size": 10,
        "page_num": 1,
    }

    second_token = with_token_response.json()["next_pagination_token"]

    last_page_response = await client.get(
        url=URL,
        params={"pagination_token": second_token},
    )
    assert last_page_response.status_code == 200
    assert len(last_page_response.json()["data"]) == 10
    assert last_page_response.json()["total_pages"] == 3
    assert last_page_response.json()["total_logs"] == 30
    assert last_page_response.json()["prev_pagination_token"] is not None
    assert last_page_response.json()["next_pagination_token"] is None
    assert last_page_response.json()["data"][-1]["body"] == {"This page number is": 0}

    prev_token = last_page_response.json()["prev_pagination_token"]
    response: None | Response = None
    while prev_token is not None:
        response = await client.get(url=URL, params={"pagination_token": prev_token})
        prev_token = response.json()["prev_pagination_token"]

    assert response.json()["prev_pagination_token"] is None
    assert response.json()["next_pagination_token"] is not None
    assert response.json()["data"][0]["body"] == {"This page number is": 29}
    assert response.json()["data"][-1]["body"] == {"This page number is": 20}


async def test__get_log_trail__invalid_pagination_token__should_raise_400(
    client: AsyncClient,
    internal_id: UUID,
    external_id: UUID,
):
    for i in range(2):
        msg = Message(
            body=orjson.dumps(
                {
                    "timestamp": datetime(year=2022, month=1, day=1 + i),
                    "internal_id": internal_id,
                    "external_id": external_id,
                    "type": "request",
                    "target_service": "some_service",
                    "content_type": "application/json",
                    "status_code": 200,
                },
            ),
            headers={
                "x-row-id": random_uuid_str(),
                "x-request-id": random_uuid_str(),
            },
        )
        async_connection_class = AsyncRabbitmq(**settings.rmq_conn())
        worker = LogsSaver(async_connection_class=async_connection_class)
        await worker.on_message(msg)

    initial_response = await client.get(
        url=URL,
        params={"page_size": 1},
    )
    assert initial_response.status_code == 200
    assert len(initial_response.json()["data"]) == 1
    assert initial_response.json()["total_pages"] == 2
    assert initial_response.json()["total_logs"] == 2
    assert initial_response.json()["prev_pagination_token"] is None
    assert initial_response.json()["next_pagination_token"] is not None

    token = b64_decode_url_params(initial_response.json()["next_pagination_token"])
    token["page_num"] = None
    lame_token = base64.b64encode(orjson.dumps(token, default=convertor)).decode()

    lame_response = await client.get(
        url=URL,
        params={"pagination_token": lame_token},
    )
    assert lame_response.status_code == 400
    assert lame_response.json() == {
        "error": {"message": "The pagination token should contain 'page_num' and 'page_size'."},
    }


async def test__get_log_trail__by_external_user__returns_only_this_user_logs(
    external_user_client: AsyncClient,
    external_user_id: UUID,
    internal_id: UUID,
    external_id: UUID,
):
    for i in range(2):
        msg = Message(
            body=orjson.dumps(
                {
                    "timestamp": datetime(year=2022, month=1, day=1 + i),
                    "internal_id": internal_id,
                    "external_id": external_id,
                    "type": "request",
                    "target_service": "some_service",
                    "content_type": "application/json",
                    "status_code": 200,
                    "external_user_id": external_user_id,
                },
            ),
            headers={
                "x-row-id": random_uuid_str(),
                "x-request-id": random_uuid_str(),
            },
        )
        async_connection_class = AsyncRabbitmq(**settings.rmq_conn())
        worker = LogsSaver(async_connection_class=async_connection_class)
        await worker.on_message(msg)

    for i in range(2):
        msg = Message(
            body=orjson.dumps(
                {
                    "timestamp": datetime(year=2022, month=1, day=1 + i),
                    "internal_id": internal_id,
                    "external_id": external_id,
                    "type": "request",
                    "target_service": "some_service",
                    "content_type": "application/json",
                    "status_code": 200,
                    "external_user_id": random_uuid_str(),
                },
            ),
            headers={
                "x-row-id": random_uuid_str(),
                "x-request-id": random_uuid_str(),
            },
        )
        async_connection_class = AsyncRabbitmq(**settings.rmq_conn())
        worker = LogsSaver(async_connection_class=async_connection_class)
        await worker.on_message(msg)

    response = await external_user_client.get(url=URL)
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2


async def test__get_log_trail__with_query_filters__should_return_correct_subsets(
    external_user_client: AsyncClient,
    external_user_id: str,
    internal_id: UUID,
    external_id: str,
):
    for i in range(5):
        msg = Message(
            body=orjson.dumps(
                {
                    "timestamp": datetime(year=2022, month=5 + i, day=1 + i),
                    "internal_id": internal_id,
                    "external_id": external_id,
                    "type": "request",
                    "target_service": "some_service",
                    "content_type": "application/json",
                    "status_code": 200 + i,
                    "body": {"While still man strives": "still he must err."},
                    "headers": None,
                    "path": "/one_way_for_all",
                    "method": "get",
                    "params": "?troll=face&still=val2",
                    "external_user_id": external_user_id,
                },
            ),
            headers={
                "x-row-id": random_uuid_str(),
                "x-request-id": random_uuid_str(),
            },
        )
        async_connection_class = AsyncRabbitmq(**settings.rmq_conn())
        worker = LogsSaver(async_connection_class=async_connection_class)
        await worker.on_message(msg)

    path_contains_response = await external_user_client.get(
        url=URL,
        params={"path__contains": "way", "type": "request"},
    )
    assert path_contains_response.status_code == 200
    assert len(path_contains_response.json()["data"]) == 5

    not_before = datetime(year=2022, month=5, day=1)
    not_after = datetime(year=2022, month=9, day=2)
    date_strict_response = await external_user_client.get(
        url=URL,
        params={
            "timestamp__gt": str(not_before),
            "timestamp__lt": str(not_after),
        },
    )
    assert date_strict_response.status_code == 200
    assert len(date_strict_response.json()["data"]) == 3

    date_permissive_response = await external_user_client.get(
        url=URL,
        params={
            "timestamp__gte": str(not_before),
            "timestamp__lte": str(not_after),
        },
    )
    assert date_permissive_response.status_code == 200
    assert len(date_permissive_response.json()["data"]) == 4

    post_methods_response = await external_user_client.get(
        url=URL,
        params={"method": "post"},
    )
    assert len(post_methods_response.json()["data"]) == 0

    response_with_201_code = await external_user_client.get(
        url=URL,
        params={"status_code": "201"},
    )
    assert len(response_with_201_code.json()["data"]) == 1
