import pytest


@pytest.mark.asyncio
async def test_get_empty_cart(client, auth_headers):
    response = await client.get("/cart/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 0


@pytest.mark.asyncio
async def test_add_item_to_cart(client, auth_headers, product):
    response = await client.post(
        "/cart/items",
        json=[{"product_id": product["id"], "quantity": 2}],
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2
    assert data["total"] == product["price"] * 2


@pytest.mark.asyncio
async def test_add_multiple_items(client, auth_headers, product, admin_headers):
    product2 = (
        await client.post(
            "/products/",
            json={
                "name": "Second Product",
                "price": 500,
                "category": "Books",
            },
            headers=admin_headers,
        )
    ).json()

    response = await client.post(
        "/cart/items",
        json=[
            {"product_id": product["id"], "quantity": 1},
            {"product_id": product2["id"], "quantity": 3},
        ],
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert len(response.json()["items"]) == 2


@pytest.mark.asyncio
async def test_update_item_quantity(client, auth_headers, product):
    add = await client.post(
        "/cart/items",
        json=[{"product_id": product["id"], "quantity": 1}],
        headers=auth_headers,
    )
    item_id = add.json()["items"][0]["id"]

    response = await client.patch(
        f"/cart/items/{item_id}",
        json={"quantity": 5},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["items"][0]["quantity"] == 5


@pytest.mark.asyncio
async def test_remove_item(client, auth_headers, product):
    add = await client.post(
        "/cart/items",
        json=[{"product_id": product["id"], "quantity": 1}],
        headers=auth_headers,
    )
    item_id = add.json()["items"][0]["id"]

    response = await client.delete(f"/cart/items/{item_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["items"] == []


@pytest.mark.asyncio
async def test_clear_cart(client, auth_headers, product):
    await client.post(
        "/cart/items",
        json=[{"product_id": product["id"], "quantity": 2}],
        headers=auth_headers,
    )

    response = await client.delete("/cart/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["items"] == []


@pytest.mark.asyncio
async def test_cart_total(client, auth_headers, product):
    await client.post(
        "/cart/items",
        json=[{"product_id": product["id"], "quantity": 3}],
        headers=auth_headers,
    )

    response = await client.get("/cart/total", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] == product["price"] * 3


@pytest.mark.asyncio
async def test_cart_unauthorized(client):
    response = await client.get("/cart/")
    assert response.status_code == 401
