# Attendance API

An API to view and get attendance details from [RIT Soft](http://rit.ac.in/ritsoft/ritsoftv2/) easily.

**The endpoint is at https://attendance-api.onrender.com/**

## API Documentation

For detailed documetation of this API, take a look at https://attendance-api.onrender.com/docs  

<br>

> <details>
> <summary> GET / : To check the status of the API</summary>
> 
> <br>
> Parameters : None
>
> Example response : 
> ```json
> {
>   "alive": "yes",
>   "message": "Check out https://attendance-api.onrender.com/docs for more details"
> }
> ```
> </details>

<br>

> <details>
> <summary> POST /login : To login and set a cookie </summary>
> <br>
>
> Parameters : None  
> Request body *(required)* : application/json  
> 
> Example body :   
> ```json
> {
>   "username": "string",
>   "password": "string"
> }
> ```
> 
> Example response :   
> ```json
> {
>   "message": "Login success. Cookie has been set successfully.",
>   "session-cookie": "c85aisn4o4k8f7phqa3e2d4em5"
> }
> ```
> 
> </details>

<br>

> <details>
> <summary>GET /login : To check login status</summary>
> 
> <br>
> 
> Parameters : session_cookie (cookie) 
> 
> Example response : 
> ```json
> {
>   "admission_no": "20BR1xx71",
>   "current_semester": "5",
>   "roll_no": "27",
>   "current_status": "APPROVED\n\t\t\t\t\t\n\n\t\t\t\t",
>   "message": "You are already logged in."
> }
> ```
> </details>
 
<br>

> <details>
> <summary>GET /attendance : To get attendance details</summary>
> 
> <br>
> 
> Parameters : session_cookie (cookie)  
> Optional parameters (query) : starting_date *(eg: 2022-06-29)*  
> Optional parameters (query) : ending_date *(eg: 2022-12-29)* 
> 
> Example reponse :
> ```json
> {
>   "name": "Devadathan M B",
>   "admission_no": "20BR1xx71",
>   "course_name": "BTECH",
>   "subject_attendance": [
>     {
>       "subject_name": "COMPUTER NETWORKS ",
>       "subject_code": "CST303",
>       "total_hours": "1",
>       "present_hours": "1",
>       "percentage": "100 %"
>     },
>     {
>       "subject_name": "DISASTER MANAGEMENT ",
>       "subject_code": "MCN301",
>       "total_hours": "12",
>       "present_hours": "12",
>       "percentage": "100 %"
>     },
>    {
>       "subject_name": "MANAGEMENT OF SOFTWARE SYSTEMS ",
>       "subject_code": "CST309",
>       "total_hours": "27",
>       "present_hours": "24",
>       "percentage": "88.89 %"
>     }
>    ...
>   ],
>   "total_attendance": " 96.59 % "
> }
> ```
> 
> </details>

<br>

> <details>
> <summary>GET /attendance/lastupdate : To get last updated details of attendance</summary>
> 
> <br>
> 
> Parameters : session_cookie (cookie)  
> <br>
> Example response :
> ```json
> {
>   "CST303": {
>     "subject_name": "COMPUTER NETWORKS ",
>     "last_update": "22, Sep 2022 Thu"
>   },
>   "MCN301": {
>     "subject_name": "DISASTER MANAGEMENT ",
>     "last_update": "08, Nov 2022 Tue"
>   },
>   "CST309": {
>     "subject_name": "MANAGEMENT OF SOFTWARE SYSTEMS ",
>     "last_update": "26, Sep 2022 Mon"
>   }
> }
> ```
> </details>

<br>

*Note that this API returns data after scraping the website, so potential bugs may be present.*  
<br>
*Also not that since this API is hosted on [render](https://render.com/docs) the initial request after a period of inactivity might take some time to process.*
