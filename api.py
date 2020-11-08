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
    return '''
    <h1>H1b Jobs Database</h1>
    <h3>You have reached: /home/</h3>
    <p>To view sample 10 entries in the database: '127.0.0.1:5000/api/v1/h1b/sample' </p>
    <p>To filter entries based on employer : '127.0.0.1:5000/api/v1/h1b?employer_name=LOGIXHUB+LLC' </p>
    <p>To filter entries based on post job title : '127.0.0.1:5000/api/v1/h1b?job_title=SOFTWARE+ENGINEER' </p>
'''

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

    query = "SELECT * FROM H1B_DATA WHERE"
    to_filter = []

    if employer_name:
        query += ' employer_name=? AND'
        to_filter.append(employer_name)

    if job_title:
        query += ' job_title=? AND'
        to_filter.append(job_title)


    if not (employer_name or job_title):
        return pageNotFound(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('h1b.db')
    conn.row_factory = dictFactory
    cur = conn.cursor()
    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)

app.run()