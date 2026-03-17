from fastapi import status

from routers.users import get_db, get_current_user
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_user(test_user):
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'codingwithricktest'
    assert response.json()['email'] == 'codingwithricktest@email.com'
    assert response.json()['first_name'] == 'Rick'
    assert response.json()['last_name'] == 'Dennison'
    assert response.json()['role'] == 'admin'
    assert response.json()['phone_number'] == '1 (505) 555-1234'


# Test change password success with test_user
def test_change_password_success(test_user):
    response = client.put("/user/password", json={"current_password": "testpassword", "new_password": "newpassword"})
    assert response.status_code == status.HTTP_204_NO_CONTENT


# Test change password invalid current password with test_user
def test_change_password_invalid_current_password(test_user):
    response = client.put("/user/password", json={"current_password": "wrongpassword", "new_password": "newpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on password change'}


# Test change phone number success with test_user
def test_change_phone_number_success(test_user):
    response = client.put( "/user/phonenumber/1 (505) 555-4321")
    assert response.status_code == status.HTTP_204_NO_CONTENT
