from pydantic import BaseModel

from enum import Enum


class Species(str, Enum):
    ALLIGATOR = "alligator"
    ANTEATER = "anteater"
    BEAR = "bear"
    BEAR_CUB = "bear cub"
    BIRD = "bird"
    BULL = "bull"
    CAT = "cat"
    CUB = "cub"
    CHICKEN = "chicken"
    COW = "cow"
    DEER = "deer"
    DOG = "dog"
    DUCK = "duck"
    EAGLE = "eagle"
    ELEPHANT = "elephant"
    FROG = "frog"
    GOAT = "goat"
    GORILLA = "gorilla"
    HAMSTER = "hamster"
    HIPPO = "hippo"
    HORSE = "horse"
    KOALA = "koala"
    KANGAROO = "kangaroo"
    LION = "lion"
    MONKEY = "monkey"
    MOUSE = "mouse"
    OCTOPUS = "octopus"
    OSTRICH = "ostrich"
    PENGUIN = "penguin"
    PIG = "pig"
    RABBIT = "rabbit"
    RHINO = "rhino"
    RHINOCEROS = "rhinoceros"
    SHEEP = "sheep"
    SQUIRREL = "squirrel"
    TIGER = "tiger"
    WOLF = "wolf"

    class Config:
        from_attributes = True

class Personality(str, Enum):
    BIG_SISTER = "big sister"
    CRANKY = "cranky"
    JOCK = "jock"
    LAZY = "lazy"
    NORMAL = "normal"
    PEPPY = "peppy"
    SISTERLY = "sisterly"
    SMUG = "smug"
    SNOOTY = "snooty"   

class Villager(BaseModel):
    villager_id: str
    name: str
    species: Species
    personality: Personality
    quote: str

    class Config:
        from_attributes = True

class Gyroid(BaseModel):
    name: str
    sound: str

class UserCreate(BaseModel):
    username: str
    native_fruit: str
    museum_complete: bool