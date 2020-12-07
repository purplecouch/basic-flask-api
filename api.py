import flask
from flask import request, jsonify
import sqlite3
import numpy as np 
from json2html import *

# Debug allows for changes to be seen in real time.
app = flask.Flask(__name__)
app.config["DEBUG"] = True

def dictFactory(cursor, row):
    """
    Function that parses the entries of the database and returns them as a list of dictionaries.
    @param cursor -- A cursor object using sqlite.
    @param row -- The row of the database being parsed.
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET'])
def homePage():
    return """
    <h1>H1b Jobs Database</h1>
    <h3>You have reached the h1b jobs database where you can query specific companies to see what salary they hired h1b workers for.</h3>
    <p> h1b salaries serve as a rough proxy of what type of jobs to expect for the same compensation. This is because the rules for posting
    h1b jobs state that the wage paid to h1b workers is required to be no lower than the prevailing wage for a given job.<p>
    
    <p> You can check to see what a given job paid by entering the information below.<br> If you know the jobs soc code enter that instead of that
    instead of the job title as it is more accurate.<br> 
    You can find list of soc codes here <a href="https://www.bls.gov/soc/2010/2010_major_groups.htm">soc codes</a> <br>
    For example the soc hob title "software developers, applications" has a code of 15-1132.<br>
    If you don't know the exact code for a job then you can write a generic title in the job title like "software engineer" or even just "software" to return
    all matches with software in the title.</p>

    <h2>Enter search information below</h2>
    <i>Note: Must enter state and county together</i>
    <form action="/h1bjobs">
             Enter Employer Name                                     <input type='text' name='employer_name'><br>
             Enter Job Title                                         <input type='text' name='job_title'><br>
             Enter soc code                                          <input type='text' name='soc_code'><br>
             Enter workiste city (example: Irvine)                   <input type='text' name='worksite_city'><br>
             Enter workiste county (example: Orange County)          <input type='text' name='worksite_county'><br>
             Enter workiste state code (Example: CA, NY, TX)         <input type='text' name='worksite_state'><br>
             <input type='submit' value='search'>
         </form>
    <br>
   

    <h2>Querying the API programatically</h2>

    <p> Example below uses python requests library </p>

    <code> import request <br>
     resp = requests.get('http://127.0.0.1:5000/api/v1/h1b',params={'employer_name':'mufg','job_title':'software engineer','worksite_city':'monterey park'})
     </code>


    """
    

@app.route('/api/v1/h1b/sample', methods=['GET'])
def api_view_sample():
    conn = sqlite3.connect('h1b.db')
    conn.row_factory = dictFactory
    cur = conn.cursor()
    sample_rows = cur.execute("SELECT * FROM h1b_data limit 2").fetchall()

    return jsonify(sample_rows)

@app.errorhandler(404)
def pageNotFound(e):
    return "<h1>Error 404</h1><p>Page not found.</p>", 404

@app.route('/h1bjobs', methods=['GET'])
def pageByFilter():
    '''
    Function that allows users to filter the results via an html form and returns output as an html table
    '''
    #query_parameters = request.args

    #employer_name = query_parameters.get('employer_name')
    #job_title = query_parameters.get('job_title')
    #soc_code = query_parameters.get('soc_code')
    #worksite_city = query_parameters.get('worksite_city')
    employer_name = request.args.get('employer_name')
    job_title = request.args.get('job_title')
    soc_code = request.args.get('soc_code')
    worksite_city = request.args.get('worksite_city')
    worksite_state = request.args.get('worksite_state')
    worksite_county = request.args.get('worksite_county')


    query = "SELECT * FROM H1B_DATA WHERE"
    qry_dtl = """select row_number() over(order by WAGE_RATE_OF_PAY_FROM desc) rownum, EMPLOYER_NAME
,WORKSITE_CITY
,WORKSITE_STATE
,WORKSITE_COUNTY
,WORKSITE_POSTAL_CODE
,max(WAGE_RATE_OF_PAY_FROM,WAGE_RATE_OF_PAY_TO) as salary
,WAGE_RATE_OF_PAY_FROM,WAGE_RATE_OF_PAY_TO
,SOC_CODE
,SOC_NAME
,JOB_TITLE from h1b_data where CASE_STATUS = 'CERTIFIED' 
AND PW_UNIT_OF_PAY = 'Year' and WAGE_UNIT_OF_PAY = 'Year' and FULL_TIME_POSITION='Y' and
 """

    to_filter = []

    if employer_name:
        employer_name = employer_name.lower()
        employer_name = '%' + employer_name + '%'
        qry_dtl += ' lower(employer_name) like ? AND'
        to_filter.append(employer_name)

    if job_title:
        job_title = job_title.lower()
        job_title = '%' + job_title + '%'
        qry_dtl += ' lower(job_title) like ? AND'
        to_filter.append(job_title)

    if soc_code:
        soc_code = soc_code.lower()
        qry_dtl += ' lower(soc_code)=? AND'
        to_filter.append(soc_code)
    
    if worksite_city:
        worksite_city = worksite_city.lower()
        qry_dtl += ' lower(worksite_city)=? AND'
        to_filter.append(worksite_city)
    
    if worksite_state:
        worksite_state = worksite_state.lower()
        qry_dtl += ' lower(worksite_state)=? AND'
        to_filter.append(worksite_state)

    if worksite_county:
        worksite_county = worksite_county.lower()
        worksite_county = '%' + worksite_county + '%'
        qry_dtl += ' lower(worksite_county) like ? AND'
        to_filter.append(worksite_county)


    if not (employer_name or (job_title or soc_code) or worksite_city or (worksite_state and worksite_county)):
        return pageNotFound(404)

    query = query[:-4] + ';'
    qry_dtl = qry_dtl[:-4] + 'order by WAGE_RATE_OF_PAY_FROM desc;'

    conn = sqlite3.connect('h1b.db')
    conn.row_factory = dictFactory
    cur = conn.cursor()
    results = cur.execute(qry_dtl, to_filter).fetchall()

    #return jsonify(results)
    #results_json = jsonify(results)
    #results_html = json2html.convert(json=results_json)
    results_html = json2html.convert(json=results)
    #for j in results:
        #results_html=json2html.convert(json=j)
        #return results_html
    return results_html

@app.route('/api/v1/h1b', methods=['GET'])
def apiViewByFilter():
    '''
    Function that allows users to filter the results in the API based on specified input.
    '''
    #query_parameters = request.args

    #employer_name = query_parameters.get('employer_name')
    #job_title = query_parameters.get('job_title')
    #soc_code = query_parameters.get('soc_code')
    #worksite_city = query_parameters.get('worksite_city')
    employer_name = request.args.get('employer_name')
    job_title = request.args.get('job_title')
    soc_code = request.args.get('soc_code')
    worksite_city = request.args.get('worksite_city')


    query = "SELECT * FROM H1B_DATA WHERE"
    qry_dtl = """select EMPLOYER_NAME
,WORKSITE_CITY
,WORKSITE_STATE
,WORKSITE_POSTAL_CODE
,max(WAGE_RATE_OF_PAY_FROM,WAGE_RATE_OF_PAY_TO) as salary
,WAGE_RATE_OF_PAY_FROM,WAGE_RATE_OF_PAY_TO
,SOC_CODE
,SOC_NAME
,JOB_TITLE from h1b_data where CASE_STATUS = 'CERTIFIED' 
AND PW_UNIT_OF_PAY = 'Year' and WAGE_UNIT_OF_PAY = 'Year' and FULL_TIME_POSITION='Y' and
 """

    to_filter = []

    if employer_name:
        employer_name = employer_name.lower()
        employer_name = '%' + employer_name + '%'
        qry_dtl += ' lower(employer_name) like ? AND'
        to_filter.append(employer_name)

    if job_title:
        job_title = job_title.lower()
        job_title = '%' + job_title + '%'
        qry_dtl += ' lower(job_title) like ? AND'
        to_filter.append(job_title)

    if soc_code:
        soc_code = soc_code.lower()
        qry_dtl += ' lower(soc_code)=? AND'
        to_filter.append(soc_code)
    
    if worksite_city:
        worksite_city = worksite_city.lower()
        qry_dtl += ' lower(worksite_city)=? AND'
        to_filter.append(worksite_city)


    if not (employer_name or (job_title or soc_code) or worksite_city):
        return pageNotFound(404)

    query = query[:-4] + ';'
    qry_dtl = qry_dtl[:-4] + 'order by WAGE_RATE_OF_PAY_FROM desc;'

    conn = sqlite3.connect('h1b.db')
    conn.row_factory = dictFactory
    cur = conn.cursor()
    results = cur.execute(qry_dtl, to_filter).fetchall()

    
    results_json = jsonify(results)
    return results_json


app.run()