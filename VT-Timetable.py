from bs4 import BeautifulSoup
from tabulate import tabulate
import requests
import argparse
import re

default_postdata = {
    'CAMPUS': '0',
    'TERMYEAR': '202301',
    'CORE_CODE': 'AR%',
    'subj_code': '',
    'CRSE_NUMBER': '',
    'crn': '',
    'open_only': '',
    'BTN_PRESSED': 'FIND class sections',
}

url = 'https://apps.es.vt.edu/ssb/HZSKVTSC.P_ProcRequest'

def get_courses(data):
    req = requests.post(url, data=data)

    soup = BeautifulSoup(req.content, 'html.parser')
    
    try:
        table = soup.find("table", class_="dataentrytable")
        rows = table.findAll("tr")
    except:
        print("No classes found!")
        return
    
    courses = list()
    
    if len(rows) > 1:
        # Remove header
        rows = rows[1:]

        for row in rows:
            cells = row.select('td')
            cells_text = list(map(lambda x: x.get_text(), cells))
            
            # Make sure the row is class information
            if len(cells_text) >= 11:
                
                # 0 - CRN
                # 1 - Course
                # 2 - Title
                # 3 - Schedule Type
                #   L = Lecture (or a combination of Lecture/Lab within the same CRN)
                #   B = LAB
                #   I = Independent Study
                #   C = Recitation
                #   R = Research
                # 4 - Modality (Face-Face / Virtual)
                # 5 - Credit Hours
                # 6 - Capacity
                # 7 - Professor
                # 8 - Days
                # 9 - Begin
                # 10 - End
                # 11 - Location
                # 12 - Exam Time
                
                courses.append([cells_text[0].strip(), 
                                cells_text[1].strip(),
                                cells_text[2].strip(),
                                cells_text[5].strip(),
                                cells_text[6].strip(),
                                cells_text[7].strip(),
                                cells_text[8].strip(),
                                cells_text[9].strip(),
                                cells_text[10].strip(),
                                cells_text[11].strip()])

    return courses


def course_search(term, subj, num, open_only):

    postdata = default_postdata.copy()

    term_year = re.split("(\d+)", term)[1]
    if "fall" in term.lower():
        term_year += "09"
    elif "spring" in term.lower():
        term_year += "01"
    elif "winter" in term.lower():
        term_year += "12"
    elif "summerii" in term.lower():
        term_year += "07"
    elif "summeri" in term.lower():
        term_year += "06"
    else:
        print("Unknown term year. Format example: fall2022, spring2023, summeri2023, summerii2023")
        return
    
    postdata['TERMYEAR'] = term_year
    postdata['subj_code'] = subj.strip().upper()
    postdata['CRSE_NUMBER'] = num.strip()
    if open_only:
        postdata['open_only'] = "on"

    courses = get_courses(postdata)
    
    col_names = ["CRN", "Course", "Title", "Credit Hours", "Seats", "Professor", "Days", "Begin", "End", "Location"]
    
    print(tabulate(courses, headers=col_names, tablefmt="fancy_grid"))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('term_year', help="Term year, e.g. fall2022, spring2023, summeri2023, summerii2023")
    parser.add_argument('subject', help="Course subject abbreviation, e.g. CS for Computer Science")
    parser.add_argument('course_number', help="Course number")
    parser.add_argument('-o', help="Show only open classes", action='store_true')
    args = parser.parse_args()
    
    term = args.term_year
    subj = args.subject
    num = args.course_number
    open_only = args.o

    course_search(term, subj, num, open_only)