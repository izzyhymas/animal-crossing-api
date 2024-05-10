from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select

from database import get_db
from dotenv import load_dotenv
import models
import schemas

import os
import requests


load_dotenv()

app = FastAPI()

base_url = "https://api.nookipedia.com"

def get_api_key():
    return os.getenv("API_KEY")

api_key = get_api_key()

headers: dict[str, str] = {
    "X-API-KEY": api_key,
    "Accepted-Version": "1.0.0"
}


villagers: list[models.Villager] = []
gyroids: list[models.Gyroid] = []
users: list[models.Users] = []

# GET
@app.get("/villagers")
async def get_villagers(species: schemas.Species, personality: schemas.Personality = None) -> list[schemas.Villager]:
    response = requests.get(f"{base_url}/villagers", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch villagers from API")
    r_json = response.json()

    filtered_villagers = []

    for villager_json in r_json:
        villager = schemas.Villager(
            villager_id=villager_json["id"],
            name=villager_json["name"],
            species=villager_json["species"].lower(),
            personality=villager_json["personality"].lower(),
            quote=villager_json["quote"]
        )
        if villager.species == species:
            if personality is None or villager.personality == personality:
                filtered_villagers.append(villager)

    return filtered_villagers

@app.get("/gyroids")
async def get_gyroids(db: Session = Depends(get_db)) -> list[schemas.Gyroid]:
    response = requests.get(f"{base_url}/nh/gyroids", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch gyroids from API")
    r_json = response.json()
    print(response)

    for gyroid_json in r_json:
        gyroid = schemas.Gyroid(
        name=gyroid_json["name"], 
        sound=gyroid_json["sound"],
        )
        gyroids.append(gyroid)
    
    return gyroids

@app.get("/fruit")
async def get_fruit() -> list[str]:
    native_fruits = ["Apple", "Cherry", "Orange", "Pear", "Peach"]
    return native_fruits

@app.get("/users")
async def get_users(db: Session = Depends(get_db)) -> list[models.Users]:
    return db.exec(select(models.Users)).all()

# POST
@app.post("/users")
async def create_user(user: models.Users, db: Session = Depends(get_db)):
    db.add(user)
    db.commit()
    return{"message": "User created successfully"}

@app.post("/users/{user_id}/villagers/{villager_id}")
async def add_villager_to_user(user_id: int, villager_id: str, db: Session = Depends(get_db)):
    user = db.get(models.Users, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    villager = db.exec(select(models.Villager).where(models.Villager.villager_id == villager_id)).first()
    if not villager:
        raise HTTPException(status_code=404, detail="Villager not found")
    
    user.villagers.append(villager)

    db.commit()

    return{"message": f"Villager '{villager.name}' added to user '{user.username}' successfully"}

@app.post("/add_villagers")
async def add_villagers_to_database(db: Session = Depends(get_db)):
    response = requests.get(f"{base_url}/villagers", headers=headers)
    r_json = response.json()

    for villager_json in r_json:
        villager = schemas.Villager(
            villager_id=villager_json["id"],
            name=villager_json["name"],
            species=villager_json["species"].lower(),
            personality=villager_json["personality"].lower(),
            quote=villager_json["quote"]
        )

        existing_villager = db.exec(select(models.Villager).where(models.Villager.villager_id == villager.villager_id)).first()
        if existing_villager:
            continue 

        villager_model = models.Villager(
            villager_id=villager.villager_id,
            name=villager.name,
            species=villager.species,
            personality=villager.personality,
            quote=villager.quote
        )
        db.add(villager_model)

    db.commit()

    return {"message": "Villagers added to database successfully"}

@app.post("/add_gyroids")
async def add_gyroids_to_database(db: Session = Depends(get_db)):
    response = requests.get(f"{base_url}/nh/gyroids", headers=headers)
    r_json = response.json()

    for gyroid_json in r_json:
        gyroid = schemas.Gyroid(
            name=gyroid_json["name"],
            sound=gyroid_json["sound"]
        )

        existing_gyroid = db.exec(select(models.Gyroid).where(models.Gyroid.gyroid_name == gyroid.name)).first()
        if existing_gyroid:
            continue 

        gyroid_model = models.Gyroid(
            gyroid_name=gyroid.name,
            sound=gyroid.sound
        )
        db.add(gyroid_model)

    db.commit()

    return {"message": "Gyroids added to database successfully"}

@app.post("/users/{user_id}/gyroids/{gyroid_name}")
async def add_gyroid_to_user(user_id: int, gyroid_name: str, db: Session = Depends(get_db)):
    user = db.get(models.Users, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    gyroid = db.exec(select(models.Gyroid).where(models.Gyroid.gyroid_name == gyroid_name)).first()
    if not gyroid:
        raise HTTPException(status_code=404, detail="Villager not found")
    
    user.gyroids.append(gyroid)

    db.commit()

    return{"message": f"Gyroid '{gyroid.gyroid_name}' added to user '{user.username}' successfully"}

# PATCH
@app.patch("/users/{user_id}")
async def update_username(user_id: int, new_username: str, db: Session = Depends(get_db)):
    user = db.get(models.Users, user_id)
    if user:
        user.username = new_username
        db.commit()
        return{"message": "Username updated successfully"}
    else:
        return HTTPException(status_code=404, detail="User not found")

@app.patch("/users/{user_id}/villagers/{old_villager_id}/switch/{new_villager_id}")
async def update_user_villagers(user_id: int, old_villager_id: str, new_villager_id: str, db: Session = Depends(get_db)):
    user = db.get(models.Users, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_villager = db.exec(select(models.Villager).where(models.Villager.villager_id == old_villager_id)).first()
    if not old_villager:
        raise HTTPException(status_code=404, detail="Old villager not found")
    
    new_villager = db.exec(select(models.Villager).where(models.Villager.villager_id == new_villager_id)).first()
    if not new_villager:
        raise HTTPException(status_code=404, detail="New villager not found")
    
    user.villagers = [villagers for villager in user.villagers if villager.villager_id != old_villager_id]

    user.villagers.append(new_villager)

    db.commit()

    return {"message": f"Villager '{old_villager.name}' switched to '{new_villager.name}' successfully"}

# DELETE
@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.Users, user_id)
    if user:
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.delete("/users/{user_id}/villagers/{villager_id}")
async def delete_villager_from_user(user_id: int, villager_id: str, db: Session = Depends(get_db)):
    user = db.get(models.Users, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    villager = db.exec(select(models.Villager).where(models.Villager.villager_id == villager_id)).first()
    if not villager:
        raise HTTPException(status_code=404, detail="Villager not found")
    
    index_to_remove = None
    for i, villager in enumerate(user.villagers):
        if villager.villager_id == villager_id:
            index_to_remove = i
            break

    if index_to_remove is not None:
        del user.villagers[index_to_remove]

    db.delete(villager)
    db.commit()
    
    return {"message": f"Villager '{villager.name}' deleted from user {user.username}' successfully"}
