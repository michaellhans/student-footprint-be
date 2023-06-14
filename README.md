# Student Carbon Footprint API Documentation

## Base URL
The base URL for all API endpoints is: `http://127.0.0.1:5000`

## Endpoints
### 1. Get CF Information of Student with NIM
- URL: `/student`
- Method: `GET`
- Description: Retrieve carbon footprint profile of  a student with a certain NIM in a certain period
- Parameters:
  - `NIM` (string): The NIM of the student
  - `start_date` (string): Start date of a period (YYYY-MM-DD)
  - `end_date` (string): End date of a period (YYYY-MM-DD)
- Example:
  ```http
  GET /student HTTP/1.1
  Host: 127.0.0.1:5000
- Response:
  ```
  {
    "data": {
        "details": {
            "cf_activity": ...,
            "cf_category": ...,
            "cf_history": [...],
            "cf_in_out": ...
        },
        "end_date": "2023-02-02",
        "start_date": "2023-01-20"
    }
  }
  ```
  
### 2. Get CF Information of Certain Major
- URL: `/major`
- Method: `GET`
- Description: Retrieve carbon footprint profile of a certain major in a certain period
- Parameters:
  - `major` (string): Major code (IF / STI / MIF)
  - `start_date` (string): Start date of a period (YYYY-MM-DD)
  - `end_date` (string): End date of a period (YYYY-MM-DD)
- Example:
  ```http
  GET /major HTTP/1.1
  Host: 127.0.0.1:5000
- Response:
  ```
  {
    "data": {
        "details": {
            "cf_activity": ...,
            "cf_category": ...,
            "cf_history": [...],
            "cf_in_out": ...,
            "cf_distribution": ...
        },
        "end_date": "2023-02-02",
        "start_date": "2023-01-20"
    }
  }
  ```

### 3. Get CF Information of ITB
- URL: `/itb`
- Method: `GET`
- Description: Retrieve carbon footprint profile of ITB in a certain period
- Parameters:
  - `start_date` (string): Start date of a period (YYYY-MM-DD)
  - `end_date` (string): End date of a period (YYYY-MM-DD)
- Example:
  ```http
  GET /itb HTTP/1.1
  Host: 127.0.0.1:5000
- Response:
  ```
  {
    "data": {
        "details": {
            "cf_activity": ...,
            "cf_category": ...,
            "cf_history": [...],
            "cf_in_out": ...,
            "cf_distribution": ...
        },
        "end_date": "2023-02-02",
        "start_date": "2023-01-20"
    }
  }
  ```

### 4. Get CF Summary
- URL: `/summary`
- Method: `GET`
- Description: Retrieve carbon footprint summary based on selected level on certain period
- Parameters:
  - `level` (string): 'student' or 'major'
  - `start_date` (string): Start date of a period (YYYY-MM-DD)
  - `end_date` (string): End date of a period (YYYY-MM-DD)
- Example:
  ```http
  GET /summary HTTP/1.1
  Host: 127.0.0.1:5000
- Response:
  ```
  {
    "data": [...CF summary per students or dates]
  }
  ```

## Prerequisites

The following is the environment preparation needed to run the application.

```
- Flask Framework for Integration
- Python 3.9.7 for Back End
```

## Installing

You can install all prerequisites package by run this command in the root directory.
```
pip install -r requirements.txt
```

## How to Run Program
1. Run `python app.py` from the root directory
2. You can use the Postman application or create simple UI to test this API

## Built With

* [Flask](https://flask.palletsprojects.com/en/1.1.x/)
* [Python](https://www.python.org/)

## Authors

- 23522011 / Michael Hans