import time
from typing import Dict, Any
from fastapi.testclient import TestClient


def test_root(test_client: TestClient) -> None:
    response = test_client.get("/api/v1/healthchecker")
    assert response.status_code == 200
    assert response.json() == {"message": "The API is LIVE!!"}


def test_create_get_coil(
    test_client: TestClient,
    coil_payload: Dict[str, Any]
) -> None:
    response = test_client.post("/api/v1/coils/", json=coil_payload)
    response_json = response.json()
    assert response.status_code == 201

    coil_id = response_json["id"]
    response = test_client.get(f"/api/v1/coils/{coil_id}")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Status"] == "Success"
    assert response_json["Coil"]["id"] is not None
    assert response_json["Coil"]["length"] == coil_payload["length"]
    assert response_json["Coil"]["weight"] == coil_payload["weight"]
    assert response_json["Coil"]["added_at"] is not None
    assert response_json["Coil"]["removed_at"] is None


def test_create_update_coil(
    test_client: TestClient,
    coil_payload: Dict[str, Any],
    coil_payload_updated: Dict[str, Any]
) -> None:
    response = test_client.post("/api/v1/coils/", json=coil_payload)
    response_json = response.json()
    assert response.status_code == 201
    coil_id = response_json["id"]

    time.sleep(1)
    response = test_client.patch(
        f"/api/v1/coils/{coil_id}", json=coil_payload_updated
    )
    response_json = response.json()
    assert response.status_code == 202
    assert response_json["Status"] == "Success"
    assert response_json["Coil"]["id"] == coil_id
    assert response_json["Coil"]["length"] == coil_payload_updated["length"]
    assert response_json["Coil"]["weight"] == coil_payload_updated["weight"]
    assert response_json["Coil"]["updated_at"] is not None
    assert (
        response_json["Coil"]["updated_at"] > response_json["Coil"]["added_at"]
    )


def test_create_delete_coil(
    test_client: TestClient,
    coil_payload: Dict[str, Any]
) -> None:
    response = test_client.post("/api/v1/coils/", json=coil_payload)
    response_json = response.json()
    assert response.status_code == 201
    coil_id = response_json["id"]

    # Delete the created coil
    response = test_client.delete(f"/api/v1/coils/{coil_id}")
    response_json = response.json()
    assert response.status_code == 202
    assert response_json["Status"] == "Success"
    assert response_json["Message"] == "Coil deleted successfully"

    # # Get the deleted coil
    # response = test_client.get(f"/api/v1/coils/{coil_id}")
    # assert response.status_code == 404
    # response_json = response.json()
    # error_msg = f"No Coil with this id: `{coil_id}` found"
    # assert response_json["detail"] == error_msg


def test_get_coil_not_found(test_client: TestClient) -> None:
    coil_id = 999
    response = test_client.get(f"/api/v1/coils/{coil_id}")
    assert response.status_code == 404
    response_json = response.json()
    error_msg = f"No Coil with this id: `{coil_id}` found"
    assert response_json["detail"] == error_msg


def test_create_coil_wrong_payload(test_client: TestClient) -> None:
    response = test_client.post("/api/v1/coils/", json={})
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json


def test_update_coil_wrong_payload(
    test_client: TestClient,
    coil_payload: Dict[str, Any]
) -> None:
    response = test_client.post("/api/v1/coils/", json=coil_payload)
    response_json = response.json()
    assert response.status_code == 201
    coil_id = response_json["id"]

    invalid_payload = {"length": "not a number", "weight": True}
    response = test_client.patch(
        f"/api/v1/coils/{coil_id}", json=invalid_payload
    )
    assert response.status_code == 422
    response_json = response.json()
    assert response_json["detail"][0]["type"] == "float_parsing"


def test_update_coil_doesnt_exist(
    test_client: TestClient,
    coil_payload_updated: Dict[str, Any]
) -> None:
    coil_id = 999
    response = test_client.patch(
        f"/api/v1/coils/{coil_id}", json=coil_payload_updated
    )
    assert response.status_code == 404
    response_json = response.json()
    error_msg = f"No Coil with this id: `{coil_id}` found"
    assert response_json["detail"] == error_msg


def test_get_coils_with_filters(
    test_client: TestClient,
    coil_payload: Dict[str, Any],
    coil_payload_updated: Dict[str, Any]
) -> None:
    test_client.post("/api/v1/coils/", json=coil_payload)
    test_client.post("/api/v1/coils/", json=coil_payload_updated)

    min_weight = coil_payload_updated["weight"] - 1
    max_weight = coil_payload_updated["weight"] + 1
    response = test_client.get(
        "/api/v1/coils/",
        params={"weight_min": min_weight, "weight_max": max_weight},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 1
    assert response_json[0]["weight"] == coil_payload_updated["weight"]
