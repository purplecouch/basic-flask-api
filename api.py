import flask
from flask import request, jsonify
import sqlite3
import numpy as np 

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
    <h3>You have reached: /home/</h3>
    <br>
    <h2>Querying the API from the browser</h2>

    <p> <b> To view sample 2 entries in the database: </b> 
    '127.0.0.1:5000/api/v1/h1b/sample' </p>

    <p> <b> To filter entries based on employer, job title/soc code and location : </b>
    '127.0.0.1:5000/api/v1/h1b?employer_name=LOGIXHUB+LLC&job_title=SOFTWARE+ENGINEER' </p>

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

@app.route('/api/v1/h1b', methods=['GET'])
def apiViewByFilter():
    '''
    Function that allows users to filter the results in the API based on specified input.
    '''
    query_parameters = request.args

    employer_name = query_parameters.get('employer_name')
    job_title = query_parameters.get('job_title')
    soc_code = query_parameters.get('soc_code')
    worksite_city = query_parameters.get('worksite_city')


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

    return jsonify(results)
    
app.run()