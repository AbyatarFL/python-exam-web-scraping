# Python Developer Coding Exam: Web Scraping for Construction Projects/Tenders

## Overview
This Python script scrapes construction project/tender details from the Melbourne City Council Planning Permit Register:  
[https://www.melbourne.vic.gov.au/planning-permit-register](https://www.melbourne.vic.gov.au/planning-permit-register)

It performs the following:

1. Extracts a list of applications within a specified date range.
2. Visits each application page and extracts all key-value pairs dynamically.
3. Saves the extracted data in **CSV, JSON, and XLSX** formats.

## Requirements
- Python 3.x
- Libraries: `selenium`, `webdriver-manager`, `openpyxl`, `csv`, `json`, `os`, `logging`, `datetime`, `time`

## Usage
1. Run the script:
    ```bash
   python python_exam_web_scraping.py
2. Enter the start and end dates in `mm/dd/yyyy` format when prompted.
3. The script opens a browser window and scrapes the data.
4. Output files are saved in the folder Output_Files:
    - `output.csv` / `details_output.csv`
    - `output.json` / `details_output.json`
    - `output.xlsx` / `details_output.xlsx`

## Notes
- Uses Selenium to automate browser interactions.
- Handles pagination and collects all records in the specified date range.
- Key-value pairs from detail pages are extracted dynamically.
- The Output_Files folder is created automatically if it does not exist.
- **Code must be adjusted if the website structure is changed.**
- **The unit test scirpt is on `/tests` directory. Can be done by using `pytest -v` on the terminal**

