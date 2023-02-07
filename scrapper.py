from fastapi import HTTPException
import requests
from bs4 import BeautifulSoup
from datetime import date
from dateutil.relativedelta import relativedelta


class Scrapper:
    # Login and set a cookie
    def login(self, username, password):
        login_url = "http://rit.ac.in/ritsoft/ritsoftv2/login.php"
        login_payload = {"username": username, "password": password, "login": "Login"}
        try:
            response = requests.post(login_url, login_payload)
            response_cookie = response.cookies["PHPSESSID"]
            response_html = response.text
            soup = BeautifulSoup(response_html, "html.parser")
            script_tags = soup.find_all("script")
            for tag in script_tags:
                if tag.string == "alert('Incorrect username or password')":
                    raise HTTPException(
                        status_code=401, detail="Invalid username or password."
                    )
        except requests.Timeout:
            raise HTTPException(
                status_code=500, detail="RIT Soft server timed out. Try again later."
            )
        return response_cookie

    # Check login
    def check_login(self, cookie):
        student_details_url = (
            "http://rit.ac.in/ritsoft/ritsoftv2/student/current_semester.php"
        )
        response_json = {}
        try:
            response_html = requests.get(
                student_details_url, cookies={"PHPSESSID": cookie}
            ).text
            soup = BeautifulSoup(response_html, "html.parser")
            if soup.script.string == "alert('Session Expired!!! Please login')":
                raise HTTPException(
                    status_code=440, detail="Session expired. Please log in again."
                )

            table_data = soup.find("form").find_all("td")
            response_json["admission_no"] = table_data[0].text
            response_json["current_semester"] = table_data[1].text
            response_json["roll_no"] = table_data[2].text
            response_json["current_status"] = table_data[3].text
            response_json["message"] = "You are already logged in."

            return response_json
        except requests.Timeout:
            raise HTTPException(
                status_code=500, detail="RIT Soft server timed out. Try again later."
            )
        except IndexError:
            raise HTTPException(status_code=404, detail="No data found")

    # Scrape the attendance data
    def scrape_attendance(self, cookie, starting_date, ending_date):
        response_json = {}

        attendance_url = "http://rit.ac.in/ritsoft/ritsoftv2/student/parent_monthly.php"
        attendance_payload = {
            "date1": starting_date,
            "date2": ending_date,
            "btnshow-new": "",
        }

        try:
            html_page = requests.post(
                attendance_url, attendance_payload, cookies={"PHPSESSID": cookie}
            ).text
        except requests.Timeout:
            raise HTTPException(
                status_code=500, detail="RIT Soft server timed out. Try again later."
            )
        soup = BeautifulSoup(html_page, "html.parser")

        if soup.script.string == "alert('Session Expired!!! Please login')":
            raise HTTPException(
                status_code=440, detail="Session expired. Please log in again."
            )
        elif soup.script.string == "alert('Data not Found')":
            raise HTTPException(status_code=404, detail="Attendance data not found.")
        else:
            try:
                name = soup.find("table").find_all("td")[0].string
                admission_no = soup.find("table").find_all("td")[1].string
                course_name = soup.find("table").find_all("td")[2].string

            except IndexError:
                raise HTTPException(status_code=404, detail="Could not find data.")

            response_json["name"] = name
            response_json["admission_no"] = admission_no
            response_json["course_name"] = course_name

            try:
                rows = soup.body.find_all(
                    "table", class_="table table-bordered table-hover"
                )[0].tbody.find_all("tr")
                subject_attendance = []
                for i in range(len(rows) - 1):
                    subject_name = (
                        rows[i].find_all("td")[0].find(text=True, recursive=False)
                    )
                    subject_code = rows[i].find_all("td")[0].sub.text
                    total_hours = rows[i].find_all("td")[1].text
                    present_hours = rows[i].find_all("td")[2].text
                    percentage = rows[i].find_all("td")[3].text
                    subject_attendance.append(
                        {
                            "subject_name": subject_name,
                            "subject_code": subject_code,
                            "total_hours": total_hours,
                            "present_hours": present_hours,
                            "percentage": percentage,
                        }
                    )
                total_attendance = rows[len(rows) - 1].find_all("td")[1].string
            except IndexError:
                raise HTTPException(
                    status_code=404, detail="Attendance data not found."
                )

            response_json["total_attendance"] = total_attendance
            response_json["subject_attendance"] = subject_attendance

            return response_json

    # Scrape last update
    def scrape_last_update(self, cookie):
        response_json = {}

        starting_date = date.today() + relativedelta(months=-6)
        ending_date = date.today()

        attendance_url = "http://rit.ac.in/ritsoft/ritsoftv2/student/parent_monthly.php"
        attendance_payload = {
            "date1": starting_date,
            "date2": ending_date,
            "btnshow-new": "",
        }

        try:
            html_page = requests.post(
                attendance_url, attendance_payload, cookies={"PHPSESSID": cookie}
            ).text
        except requests.Timeout:
            raise HTTPException(
                status_code=500, detail="RIT Soft server timed out. Try again later."
            )
        soup = BeautifulSoup(html_page, "html.parser")

        if soup.script.string == "alert('Session Expired!!! Please login')":
            raise HTTPException(
                status_code=440, detail="Session expired. Please log in again."
            )
        elif soup.script.string == "alert('Data not Found')":
            raise HTTPException(status_code=404, detail="Attendance data not found.")
        else:
            try:
                subject_code_list = []
                rows = soup.body.find_all(
                    "table", class_="table table-bordered table-hover"
                )[0].tbody.find_all("tr")
                for i in range(len(rows) - 1):
                    subject_code = rows[i].find_all("td")[0].sub.text
                    subject_code_list.append(subject_code)

                rows = soup.find(id="status-t").tbody.find_all("tr")
                if rows == None or len(rows) == 1:
                    raise HTTPException(
                        status_code=404, detail="No last update data found."
                    )
                for code in subject_code_list:
                    for row in rows:
                        subject_code_element = row.find_all("td")[3].sub
                        subject_code = subject_code_element.text
                        if code == subject_code:
                            response_json[code] = {}
                            response_json[code]["subject_name"] = row.find_all("td")[
                                3
                            ].find(text=True, recursive=False)
                            response_json[code]["last_update"] = row.find_all("td")[
                                1
                            ].text
                            break
                return response_json

            except IndexError:
                raise HTTPException(
                    status_code=404, detail="Last update data not found."
                )

    # Scrape absent details
    def scrape_absent(self, cookie):
        response_json = []

        starting_date = date.today() + relativedelta(months=-6)
        ending_date = date.today()

        attendance_url = "http://rit.ac.in/ritsoft/ritsoftv2/student/parent_monthly.php"
        attendance_payload = {
            "date1": starting_date,
            "date2": ending_date,
            "btnshow-new": "",
        }

        try:
            html_page = requests.post(
                attendance_url, attendance_payload, cookies={"PHPSESSID": cookie}
            ).text
        except requests.Timeout:
            raise HTTPException(
                status_code=500, detail="RIT Soft server timed out. Try again later."
            )
        soup = BeautifulSoup(html_page, "html.parser")

        if soup.script.string == "alert('Session Expired!!! Please login')":
            raise HTTPException(
                status_code=440, detail="Session expired. Please log in again."
            )
        elif soup.script.string == "alert('Data not Found')":
            raise HTTPException(status_code=404, detail="Absent data not found.")
        else:
            try:
                rows = soup.body.find_all(
                    "table", class_="table table-bordered table-hover"
                )[1].tbody.find_all("tr")

                if rows == None or len(rows) == 1:
                    raise HTTPException(
                        status_code=404,
                        detail="Attendance data not found",
                    )

                for row in rows:
                    cols = row.find_all("td")
                    attendance_date = cols[1].string
                    hour = cols[2].string
                    subject_name = cols[3].find(text=True, recursive=False)
                    subject_code = cols[3].find("sub").string
                    status = cols[4].string

                    if status == "PRESENT":
                        continue

                    response_json.append(
                        {
                            "subject_name": subject_name,
                            "subject_code": subject_code,
                            "absent_date": attendance_date,
                            "absent_hour": hour,
                            "status": status,
                        }
                    )
                if len(response_json) == 0:
                    HTTPException(status_code=404, detail="No absent hours")
                return response_json

            except IndexError:
                raise HTTPException(status_code=404, detail="Absent data not found")
