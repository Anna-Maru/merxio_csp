import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post(
        "/auth/register",
        json={
            "full_name": "Иван Иванов",
            "email": "ivan@example.com",
            "phone": "+71234567891",
            "password": "ValidPass!",
            "password_confirm": "ValidPass!",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "ivan@example.com"
    assert data["phone"] == "+71234567891"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client, registered_user):
    response = await client.post(
        "/auth/register",
        json={
            "full_name": "Other User",
            "email": "test@example.com",
            "phone": "+79876543210",
            "password": "ValidPass!",
            "password_confirm": "ValidPass!",
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_duplicate_phone(client, registered_user):
    response = await client.post(
        "/auth/register",
        json={
            "full_name": "Other User",
            "email": "other@example.com",
            "phone": "+71234567890",
            "password": "ValidPass!",
            "password_confirm": "ValidPass!",
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_invalid_password_no_upper(client):
    response = await client.post(
        "/auth/register",
        json={
            "full_name": "Test",
            "email": "test2@example.com",
            "phone": "+71111111111",
            "password": "nouppercase!",
            "password_confirm": "nouppercase!",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_password_no_special(client):
    response = await client.post(
        "/auth/register",
        json={
            "full_name": "Test",
            "email": "test3@example.com",
            "phone": "+72222222222",
            "password": "NoSpecialChar",
            "password_confirm": "NoSpecialChar",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_phone(client):
    response = await client.post(
        "/auth/register",
        json={
            "full_name": "Test",
            "email": "test4@example.com",
            "phone": "89001234567",
            "password": "ValidPass!",
            "password_confirm": "ValidPass!",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_passwords_mismatch(client):
    response = await client.post(
        "/auth/register",
        json={
            "full_name": "Test",
            "email": "test5@example.com",
            "phone": "+73333333333",
            "password": "ValidPass!",
            "password_confirm": "OtherPass!",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_by_email(client, registered_user):
    response = await client.post(
        "/auth/login",
        json={
            "login": "test@example.com",
            "password": "TestPass!",
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_by_phone(client, registered_user):
    response = await client.post(
        "/auth/login",
        json={
            "login": "+71234567890",
            "password": "TestPass!",
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client, registered_user):
    response = await client.post(
        "/auth/login",
        json={
            "login": "test@example.com",
            "password": "WrongPass!",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    response = await client.post(
        "/auth/login",
        json={
            "login": "nobody@example.com",
            "password": "ValidPass!",
        },
    )
    assert response.status_code == 401
