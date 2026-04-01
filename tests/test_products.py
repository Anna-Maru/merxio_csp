import pytest


@pytest.mark.asyncio
async def test_get_products_unauthorized(client):
    response = await client.get("/products/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_products_authorized(client, auth_headers, product):
    response = await client.get("/products/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_create_product_as_admin(client, admin_headers):
    response = await client.post("/products/", json={
        "name": "New Product",
        "description": "Description",
        "price": 500,
        "category": "Books",
    }, headers=admin_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "New Product"


@pytest.mark.asyncio
async def test_create_product_as_user(client, auth_headers):
    response = await client.post("/products/", json={
        "name": "Forbidden",
        "price": 100,
    }, headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_product(client, admin_headers, product):
    response = await client.put(f"/products/{product['id']}", json={
        "price": 2000,
    }, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["price"] == 2000


@pytest.mark.asyncio
async def test_delete_product(client, admin_headers, product):
    response = await client.delete(
        f"/products/{product['id']}", headers=admin_headers
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_filter_by_category(client, auth_headers, product):
    response = await client.get(
        "/products/?category=Electronics", headers=auth_headers
    )
    assert response.status_code == 200
    assert all(p["category"] == "Electronics" for p in response.json())


@pytest.mark.asyncio
async def test_filter_by_price(client, auth_headers, product):
    response = await client.get(
        "/products/?min_price=500&max_price=1500", headers=auth_headers
    )
    assert response.status_code == 200
    for p in response.json():
        assert 500 <= p["price"] <= 1500


@pytest.mark.asyncio
async def test_search_by_name(client, auth_headers, product):
    response = await client.get(
        "/products/?search=Test", headers=auth_headers
    )
    assert response.status_code == 200
    assert any("Test" in p["name"] for p in response.json())
    