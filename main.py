from fastapi import FastAPI, Response, Cookie, HTTPException
from pydantic import BaseModel
from scrapper import Scrapper
from typing import Union
from datetime import date
from dateutil.relativedelta import relativedelta

description = """
Attendance API helps you grab your attendance details from RIT Soft quickly and easily.  

## What can this API do?

This API can do whatever things you can do in RIT Soft basically. But currently only specific endpoints are implemented.  

As of now the you will be able to :

* **Login** remotely
* **View basic student information**
* **Get attendance details of your current semester**

"""

tags_metadata = [
    {
        "name": "status",
        "description": "Check the status of the API. If it's alive or not.",
    },
    {"name": "login", "description": "Allows you to login."},
    {"name": "attendance", "description": "View attendance details (after logging in)"},
]

app = FastAPI(
    title="Attendance API", description=description, openapi_tags=tags_metadata
)
scrapper = Scrapper()


class User(BaseModel):
    username: str
    password: str


@app.get("/", tags=["status"])
def is_alive():
    return {"alive": "yes"}


@app.get("/login", tags=["login"])
def is_logged_in(session_cookie: str = Cookie(None)):
    if not session_cookie:
        raise HTTPException(status_code=401, detail="You are not logged in.")
    else:
        return scrapper.check_login(session_cookie)


@app.post("/login", tags=["login"])
def login(response: Response, user: User):
    cookie = scrapper.login(user.username, user.password)
    response.set_cookie(key="session_cookie", value=cookie)
    return {
        "message": "Login success. Cookie has been set successfully.",
        "session-cookie": cookie,
    }


@app.get("/attendance", tags=["attendance"])
def get_attendance(
    session_cookie: str = Cookie(None),
    starting_date: date = date.today() + relativedelta(months=-6),
    ending_date: date = date.today(),
):
    if not session_cookie:
        raise HTTPException(
            status_code=401, detail="Not logged in. Please log in and try again."
        )
    else:
        return scrapper.scrape_attendance(session_cookie, starting_date, ending_date)
