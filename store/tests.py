import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from store.models import Customer   # adjust app name


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="imran",
        password="test1234"
    )

@pytest.fixture
def bearer_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

@pytest.fixture
def auth_client(api_client, bearer_token):
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {bearer_token}"
    )
    return api_client


@pytest.mark.django_db
def test_create_customer_success(auth_client):
    url = reverse("customer-create")

    payload = {
        "name": "ABC Corporation",
        "email": "abc@test.com",
        "phone": "01700000000"
    }

    response = auth_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["message"] == "Customer created successfully"
    assert Customer.objects.count() == 1


@pytest.mark.django_db
def test_create_customer_invalid_data(auth_client):
    url = reverse("customer-create")

    response = auth_client.post(
        url,
        {"name": ""},
        format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.data

@pytest.mark.django_db
def test_create_customer_unauthorized(api_client):
    url = reverse("customer-create")

    response = api_client.post(
        url,
        {"name": "Unauthorized"},
        format="json"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_create_customer_invalid_token(api_client):
    api_client.credentials(
        HTTP_AUTHORIZATION="Bearer invalidtoken"
    )

    url = reverse("customer-create")

    response = api_client.post(
        url,
        {"name": "Invalid Token"},
        format="json"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

