from fastapi import FastAPI, Response, Cookie, HTTPException
from pydantic import BaseModel
from scrapper import Scrapper
from typing import Union
from datetime import date
from dateutil.relativedelta import relativedelta

description = """
Attendance API helps you grab your attendance details from RIT Soft quickly and easily.  

## What can this API do?

This API can do :

* **Login remotely**
* **View basic student information**
* **Get attendance details of your current semester**
* **View last updated attendance dates of subjects**
* **Get detailed attendance details including absent and present dates(_not implemented_)**

"""

tags_metadata = [
    {
        "name": "status",
        "description": "To check the status of the API.",
    },
    {"name": "login", "description": "To login."},
    {
        "name": "attendance",
        "description": "To view attendance details (_after logging in_)",
    },
]

app = FastAPI(
    title="Attendance API", description=description, openapi_tags=tags_metadata
)
scrapper = Scrapper()


class User(BaseModel):
    username: str
    password: str


@app.get(
    "/",
    tags=["status"],
    summary="Check status of API",
    response_description="Returns a json object with alive = true on success",
)
def is_alive():
    return {
        "alive": "yes",
        "message": "Check out https://attendance-api.onrender.com/docs for more details",
    }


@app.get(
    "/login",
    tags=["login"],
    summary="Check logged in status",
    response_description="Returns a json object with basic student details on success",
)
def is_logged_in(
    session_cookie: str = Cookie(None),
):
    if not session_cookie:
        raise HTTPException(status_code=401, detail="You are not logged in.")
    else:
        return scrapper.check_login(session_cookie)


@app.post(
    "/login",
    tags=["login"],
    summary="Log in and generate a cookie",
    response_description="Returns a json object with a cookie on success",
)
def login(
    response: Response,
    user: User,
):
    cookie = scrapper.login(user.username, user.password)
    response.set_cookie(key="session_cookie", value=cookie)
    return {
        "message": "Login success. Cookie has been set successfully.",
        "session-cookie": cookie,
    }


@app.get(
    "/attendance",
    tags=["attendance"],
    summary="View attendance details",
    response_description="Returns a json object with basic student details and attendance details of the student on success",
)
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


@app.get(
    "/attendance/lastupdate",
    tags=["attendance"],
    summary="View last attendance update details",
    response_description="Returns a json object with subjects and their last attendance update details on success",
)
def get_last_update(
    session_cookie: str = Cookie(None),
):
    if not session_cookie:
        raise HTTPException(
            status_code=401, detail="Not logged in. Please log in and try again."
        )
    else:
        return scrapper.scrape_last_update(session_cookie)
