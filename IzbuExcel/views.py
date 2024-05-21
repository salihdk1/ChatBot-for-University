"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from IzbuExcel import app

@app.route('/')
def index():
    return render_template('index.html')