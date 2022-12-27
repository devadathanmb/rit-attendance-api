from fastapi import HTTPException
import requests
from bs4 import BeautifulSoup
from datetime import date
from dateutil.relativedelta import relativedelta

class Scrapper():
    
    # Login and generate a cookie
    def login(self, username, password):
        login_url = "http://rit.ac.in/ritsoft/ritsoftv2/login.php"
        login_payload = {"username" : username, "password" : password, "login" : "Login"}
        try:
            response_cookie = requests.post(login_url, login_payload).cookies["PHPSESSID"]
        except requests.Timeout:
            raise HTTPException(status_code=500, detail="RIT Soft server timed out. Try again later")
        return response_cookie
    
    # Scrape the attendance data
    def scrapedata(self, cookie):
        response_json = {}

        attendance_url = "http://rit.ac.in/ritsoft/ritsoftv2/student/parent_monthly.php"
        attendance_payload = {"date1" : date.today() + relativedelta(months=-6), "date2" : date.today(), "btnshow-new" : ""}

        html_page = requests.post(attendance_url, attendance_payload, cookies={"PHPSESSID" : cookie}).text
        soup = BeautifulSoup(html_page, "html.parser")

        if soup.script.string == "alert('Session Expired!!! Please login')" :
            raise HTTPException(status_code=401, detail="Invalid username or password")
        else:
            name = soup.find("table").find_all("td")[0].string
            admission_no = soup.find("table").find_all("td")[1].string
            course_name = soup.find("table").find_all("td")[2].string

            if None in (name, admission_no, course_name):
                raise HTTPException(status_code=404, detail="Could not find data.")

            response_json["name"] = name
            response_json["admission_no"] = admission_no
            response_json["course_name"] = course_name

            rows = (soup.body.find_all("table", class_ = "table table-bordered table-hover")[0].tbody.find_all("tr"))
            subject_attendance = []
            for i in range(len(rows) - 1): 
                subject_name = rows[i].find_all("td")[0].find(text=True, recursive=False)
                subject_code = rows[i].find_all("td")[0].sub.text
                total_hours = rows[i].find_all("td")[1].text
                present_hours = rows[i].find_all("td")[2].text
                percentage = rows[i].find_all("td")[3].text
                subject_attendance.append({"subject_name" : subject_name, "subject_code" : subject_code, "total_hours" : total_hours, "present_hours" : present_hours, "percentage" : percentage})

            if not subject_attendance:
                raise HTTPException(status_code=404, detail="No attendance record found")

            total_attendance = rows[len(rows) - 1].find_all("td")[1].string
            response_json["subject_attendance"] = subject_attendance
            response_json["total_attendance"] = total_attendance

            return response_json
