from fastapi import FastAPI
from pydantic import BaseModel
from scrapper import Scrapper
from typing import Union
from datetime import date

app = FastAPI()
scrapper = Scrapper()

class User(BaseModel):
    username: str
    password: str
    starting_date: Union[date, None]
    ending_date: Union[date, None]

@app.get("/")
def is_alive():
    return {"alive": "yes"}

@app.post("/attendance")
def get_attendance(user: User):
    cookie = scrapper.login(user.username, user.password) 
    return scrapper.scrape_attendance(cookie, user.starting_date, user.ending_date)

