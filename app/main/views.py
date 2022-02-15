from flask import render_template, session, redirect, url_for, current_app
from . import main

@main.route('/', methods=['GET', 'POST'])
def index():
    return '<h1>Hello World!</h1>'