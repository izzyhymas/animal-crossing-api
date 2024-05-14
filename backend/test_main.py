from fastapi.testclient import TestClient
import pytest
from unittest.mock import MagicMock, patch
from sqlmodel import create_engine, Session
import database
from main import app
import models


client = TestClient(app)


def test_get_villagers():
    with patch("main.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {
                "id": "cat00",
                "name": "Bob",
                "species": "cat",
                "personality": "lazy",
                "quote": "You only live once...or nine times."
            }
        ]

        response = client.get(f"/villagers?species=cat&personality=lazy")

        assert response.status_code == 200

        expected_response = [
            {
                "villager_id": "cat00",
                "name": "Bob",
                "species": "cat",
                "personality": "lazy",
                "quote": "You only live once...or nine times."
            }
        ]
        assert response.json() == expected_response

def test_get_gyroids():
    with patch("main.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {
                "name": "bubbloid",
                "sound": "Melody"
            }
        ]
        
        response = client.get("/gyroids")

        assert response.status_code == 200

        expected_response = [
            {
                "name": "bubbloid",
                "sound": "Melody"
            }
        ]
        assert response.json() == expected_response

@pytest.fixture
def db_session():
    session = MagicMock(spec=Session)
    return session

@pytest.fixture
def override_get_db(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[database.get_db] = _override_get_db
    yield
    app.dependency_overrides.pop(database.get_db)

def test_get_users(override_get_db, db_session):
    user1 = models.Users(user_id = 1, username="user1", native_fruit="Apple")
    user2 = models.Users(user_id = 2, username="user2", native_fruit="Cherry")

    db_session.exec.return_value.all.return_value = [user1, user2]

    result = client.get("/users")

    assert result == result

    response = client.get("/users")

    assert response.status_code == 200
    
    expected_users = [
        {"user_id": 1, "username": "user1", "native_fruit": "Apple"},
        {"user_id": 2, "username": "user2", "native_fruit": "Cherry"}
    ]
    assert response.json() == expected_users

def test_create_user(override_get_db, db_session):
    user_data = {"user_id": 10, "username": "testuser", "native_fruit": "Apple"}

    response = client.post("/users", json=user_data)

    assert response.status_code == 200

    assert response.json() == {"message": "User created successfully"}

    created_user = db_session.add.call_args[0][0]
    assert created_user.user_id == user_data["user_id"]
    assert created_user.username == user_data["username"]
    assert created_user.native_fruit == user_data["native_fruit"]

def test_add_villager_to_user(override_get_db, db_session):
    user_id = 1
    user = models.Users(user_id=user_id, username="user1", native_fruit="Apple")

    villager_id = "cat00"
    villager = models.Villager(
        villager_id=villager_id,
        name="Bob",
        species="cat",
        personality="lazy",
        quote="You only live once...or nine times."
    )

    db_session.get.return_value = user
    db_session.exec.return_value.first.return_value = villager

    response = client.post(f"/users/{user_id}/villagers/{villager_id}")

    assert response.status_code == 200

    assert response.json() == {"message": f"Villager '{villager.name}' added to user '{user.username}' successfully"}

    assert villager in user.villagers
    db_session.commit.assert_called_once()

def test_add_villagers_to_database(override_get_db, db_session):
    with patch("main.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {
                "id": "cat00",
                "name": "Bob",
                "species": "cat",
                "personality": "lazy",
                "quote": "You only live once...or nine times."
            },
            {
                "id": "cat08",
                "name": "Moe",
                "species": "cat",
                "personality": "lazy",
                "quote": "Ignorance is bliss."
            }
        ]
        response = client.post("/add_villagers")

        assert response.status_code == 200

        assert response.json() == {"message": "Villagers added to database successfully"}

        db_session.commit.assert_called_once()

def test_add_gyroids_to_database(override_get_db, db_session): 
    with patch("main.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {"name": "aluminoid", "sound":"Drum set"},
            {"name": "brewstoid", "sound": "Snare"}
        ]
        response = client.post("/add_gyroids")

        assert response.status_code == 200

        assert response.json() == {"message": "Gyroids added to database successfully"}

        db_session.commit.assert_called_once()

def test_add_gyroid_to_user(override_get_db, db_session):
    user_id = 1
    user = models.Users(user_id=user_id, username="user1", native_fruit="Apple")

    gyroid_name = "brewstoid"
    gyroid = models.Gyroid(
        gyroid_name=gyroid_name,
        sound="Snare"
    )

    db_session.get.return_value = user
    db_session.exec.return_value.first.return_value = gyroid

    response = client.post(f"/users/{user_id}/gyroids/{gyroid_name}")

    assert response.status_code == 200

    assert response.json() == {"message": f"Gyroid '{gyroid.gyroid_name}' added to user '{user.username}' successfully"}

    assert gyroid in user.gyroids
    db_session.commit.assert_called_once()

def test_update_username(override_get_db, db_session):
    user_id = 1
    old_username = "user1"
    new_username = "new_user_1"
    user = models.Users(
        user_id=user_id,
        username=old_username,
        native_fruit="Apple"
    )
    db_session.get.return_value = user

    response = client.patch(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json() == {"message": "Username updated successfully"}

    assert user.username == new_username
    db_session.commit.assert_called_once()

def test_update_user_villagers(override_get_db, db_session):
    user_id = 1
    old_villager_id = "cat00"
    new_villager_id = "cat21"
    old_villager_name = "Bob"
    new_villager_name = "Katt"
    user = models.Users(
        user_id=user_id,
        username="user1",
        native_fruit="Apple"
    )
    old_villager = models.Villager(
        villager_id=old_villager_id,
        name=old_villager_name,
        species="cat",
        personality="lazy",
        quote="You only live once...or nine times."
    )
    new_villager = models.Villager(
        villager_id=new_villager_id,
        name=new_villager_name,
        species="cat",
        personality="big sister",
        quote="MeowMEOWmeow!"
    )

    db_session.get.return_value = user
    db_session.exec.return_value.first.side_effect = [old_villager, new_villager]

    response = client.patch(f"/users/{user_id}/villagers/{old_villager_id}/switch/{new_villager_id}")

    assert response.status_code == 200

    expected_message = f"Villager '{old_villager.name}' switched to '{new_villager.name}' successfully"
    assert response.json() == {"message": expected_message}

    assert old_villager not in user.villagers
    assert new_villager in user.villagers
    db_session.commit.assert_called_once()

def test_delete_user(override_get_db, db_session):
    user_id = 1
    username = "user1"
    user = models.Users(
        user_id=user_id,
        username=username,
        native_fruit="Apple"
    )

    db_session.get.return_value = user

    response = client.delete(f"/users/{user_id}")

    assert response.status_code == 200

    assert response.json() == {"message": "User deleted successfully"}

    db_session.delete.assert_called_once_with(user)
    db_session.commit.assert_called_once()

def test_delete_villager_from_user(override_get_db, db_session):
    user_id = 1
    villager_id = "cat00"
    villager_name = "Bob"
    user = models.Users(
        user_id=user_id,
        username="user1",
        native_fruit="Apple"
    )
    villager = models.Villager(
        villager_id=villager_id,
        villager_name=villager_name,
        species="cat",
        personality="lazy",
        quote="You only live once...or nine times."
    )

    user.villagers.append(villager)

    db_session.get.return_value = user

    response = client.delete(f"/users/{user_id}/villagers/{villager_id}")

    assert response.status_code == 200

    assert response.json() == {"message": f"Villager '{villager.name}' deleted from user {user.username}' successfully"}

    assert villager not in user.villagers
    db_session.delete.assert_called_once_with(villager)
    db_session.commit.assert_called_once()


def main():
    test_get_villagers()
    test_get_gyroids()
    test_get_users()
    test_create_user()
    test_add_villager_to_user()
    test_add_villagers_to_database()
    test_add_gyroids_to_database()
    test_add_gyroid_to_user()
    test_update_username()
    test_update_user_villagers()
    test_delete_user()
    test_delete_villager_from_user()

if __name__ == "__main__":
    main()