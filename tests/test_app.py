# unit tests for app.py
import os
if os.path.exists("env.py"):
    import env


def test_index(app, client):
    """
    GIVEN a running Flask app
    WHEN the client browses to /
    THEN check for status code 200
    """
    res = client.get('/')
    assert res.status_code == 200


def test_index_content(app, client):
    """
    GIVEN a running Flask app
    WHEN the client browses to /
    THEN check for <div class="card  in the returned data: this indicates that the template has been filled with data from the db
    """
    res = client.get('/')
    assert b'<div class="card' in res.data


def test_get_books(app, client):
    """
    GIVEN a running Flask app
    WHEN the client browses to /get_books
    THEN check for status code 200
    """
    res = client.get('/get_books')
    assert res.status_code == 200


def test_get_books_content(app, client):
    """
    GIVEN a running Flask app
    WHEN the client browses to /get_books
    THEN check for '<div class="card' in the returned data: this indicates that the template has been filled with data from the db
    """
    res = client.get('/get_books')
    assert b'<div class="card' in res.data


def test_register(app, client):
    """
    GIVEN a running Flask app
    WHEN the client browses to /register
    THEN check for status code 200
    """
    res = client.get('/register')
    assert res.status_code == 200


def test_register_content(app, client):
    """
    GIVEN a running Flask app
    WHEN the client browses to /register
    THEN check the h1 element with class "card-title" and text "Register Your Account"
    """
    res = client.get('/register')
    assert b'<h1 class="card-title">Register Your Account</h1>' in res.data


def test_login(app, client):
    """
    GIVEN a running Flask app
    WHEN the client browses to /login
    THEN check for status code 200
    """
    res = client.get('/login')
    assert res.status_code == 200


def test_login_content(app, client):
    """
    GIVEN a running Flask app
    WHEN the client browses to /login
    THEN check the h1 element with class "card-title" and text "Log In To Your Account"
    """
    res = client.get('/login')
    assert b'<h1 class="card-title">Log In To Your Account</h1>' in res.data
