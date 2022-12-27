from fastapi import FastAPI
from pydantic import BaseModel
from scrapper import Scrapper

app = FastAPI()
scrapper = Scrapper()

class User(BaseModel):
    username: str
    password: str

@app.get("/")
def is_alive():
    return {"alive": "yes"}

@app.post("/attendance")
def get_attendance(user: User):
    cookie = scrapper.login(user.username, user.password) 
    return scrapper.scrapedata(cookie)

