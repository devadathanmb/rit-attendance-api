from fastapi import FastAPI, Response, Cookie, HTTPException
from pydantic import BaseModel
from scrapper import Scrapper
from typing import Union
from datetime import date
from dateutil.relativedelta import relativedelta

app = FastAPI()
scrapper = Scrapper()

class User(BaseModel):
    username: str
    password: str

@app.get("/")
def is_alive():
    return {"alive": "yes"}

@app.get("/login")
def is_logged_in(session_cookie: str = Cookie(None)):
    if not session_cookie:
        raise HTTPException(status_code=401, detail = "You are not logged in.")
    else:
        return scrapper.check_login(session_cookie)
    
@app.post("/login")
def login(response: Response, user: User):
    cookie = scrapper.login(user.username, user.password)
    response.set_cookie(key="session_cookie", value=cookie) 
    return {"message" : "Login success. Cookie has been set successfully.", "session-cookie" : cookie}
    
@app.get("/attendance")
def get_attendance(session_cookie: str = Cookie(None), starting_date: date = date.today() + relativedelta(months=-6), ending_date: date = date.today()):
    if not session_cookie:
        raise HTTPException(status_code = 401, detail = "Not logged in. Please log in and try again.")
    else:
        return scrapper.scrape_attendance(session_cookie, starting_date, ending_date)

