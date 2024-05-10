from sqlalchemy.orm import Session

import models
import schemas

def create_villager(db: Session, villager: schemas.Villager):
    db_villager = models.Villager(**villager.model_dump())
    db.add(db_villager)
    db.commit()
    db.refresh(db_villager)
    return db_villager

def get_villager(db: Session):
    return db.query(models.Villager).all()