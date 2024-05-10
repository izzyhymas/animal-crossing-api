from sqlmodel import Field, Relationship, SQLModel


class UserVillagerLink(SQLModel, table=True):
    user_id: int = Field(foreign_key="users.user_id", primary_key=True)
    villager_id: str = Field(foreign_key="villager.villager_id", primary_key=True)

class Villager(SQLModel, table=True):
    villager_id: str = Field(primary_key=True)
    name: str
    species: str
    personality: str
    quote: str
    users: list["Users"] = Relationship(back_populates="villagers", link_model=UserVillagerLink)

class UserGyroidLink(SQLModel, table=True):
    user_id: int = Field(foreign_key="users.user_id", primary_key=True)
    gyroid_name: str = Field(foreign_key="gyroid.gyroid_name", primary_key=True)

class Gyroid(SQLModel, table=True):
    gyroid_name: str = Field(primary_key=True)
    sound: str
    users: list["Users"] = Relationship(back_populates="gyroids", link_model=UserGyroidLink)

class Users(SQLModel, table=True):
    user_id: int = Field(primary_key=True)
    username: str
    native_fruit: str
    gyroids: list[Gyroid] = Relationship(back_populates="users", link_model=UserGyroidLink)
    villagers: list[Villager] = Relationship(back_populates="users", link_model=UserVillagerLink)