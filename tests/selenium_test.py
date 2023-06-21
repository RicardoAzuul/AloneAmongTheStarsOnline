import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


chrome_driver = webdriver.Chrome(r'dev\chromedriver.exe')
chrome_driver.maximize_window()


def test_webapp_title():
    """
    GIVEN a running Heroku app
    WHEN the client browses to /
    THEN check the title is "Bookable"
    """    
    chrome_driver.get('https://code-institute-ms3-book-review.herokuapp.com/')

    title = "Bookable"
    assert title == chrome_driver.title


def test_webapp_register_existing_user():
    """
    GIVEN an existing username
    WHEN the client tries to register the existing username
    THEN check for the "Sorry, your username has already been taken!" flash message
    """    
    chrome_driver.get('https://code-institute-ms3-book-review.herokuapp.com/register')

    existing_user = "hank.schrader"
    password = "Passw0rd"

    username_element = chrome_driver.find_element(By.NAME, "username")
    password_element = chrome_driver.find_element(By.NAME, "password")
    register_button = chrome_driver.find_element(By.CLASS_NAME, "btn-primary")

    username_element.send_keys(existing_user)
    password_element.send_keys(password)
    register_button.click()

    assert "Sorry, your username has already been taken!" in chrome_driver.page_source


def test_webapp_brand_nav():
    """
    GIVEN a running Heroku app
    WHEN the client clicks the brand nav
    THEN check the url ends with get_books
    """    
    chrome_driver.get('https://code-institute-ms3-book-review.herokuapp.com/')

    url = "https://code-institute-ms3-book-review.herokuapp.com/get_books"

    brand_href = chrome_driver.find_element(By.CLASS_NAME, "navbar-brand")
    brand_href.click()

    assert url == chrome_driver.current_url

# idea from code from https://stackoverflow.com/questions/12323403/how-do-i-find-an-element-that-contains-specific-text-in-selenium-webdriver-pyth
def test_webapp_all_books_nav():
    """
    GIVEN a running Heroku app
    WHEN the client clicks the All Books button
    THEN check the url ends with get_books
    """    
    chrome_driver.get('https://code-institute-ms3-book-review.herokuapp.com/')

    url = "https://code-institute-ms3-book-review.herokuapp.com/get_books"

    all_books_href = chrome_driver.find_element(By.XPATH, "//a[text()='All Books ']")
    all_books_href.click()

    assert url == chrome_driver.current_url


def test_webapp_log_in_nav():
    """
    GIVEN a running Heroku app
    WHEN the client clicks the Log In nav
    THEN check the url ends with login
    """    
    chrome_driver.get('https://code-institute-ms3-book-review.herokuapp.com/')

    url = "https://code-institute-ms3-book-review.herokuapp.com/login"

    log_in_href = chrome_driver.find_element(By.XPATH, "//a[text()='Log In']")
    log_in_href.click()

    assert url == chrome_driver.current_url


def test_webapp_register_nav():
    """
    GIVEN a running Heroku app
    WHEN the client clicks the Register nav
    THEN check the url ends with register
    """    
    chrome_driver.get('https://code-institute-ms3-book-review.herokuapp.com/')

    url = "https://code-institute-ms3-book-review.herokuapp.com/register"

    register_href = chrome_driver.find_element(By.XPATH, "//a[text()='Register']")
    register_href.click()

    assert url == chrome_driver.current_url


def test_webapp_log_in_url():
    """
    GIVEN a running Heroku app
    WHEN the client clicks the Log In link at the bottom of the Register page
    THEN check the url ends with login
    """    
    chrome_driver.get('https://code-institute-ms3-book-review.herokuapp.com/register')

    url = "https://code-institute-ms3-book-review.herokuapp.com/login"

    login_href = chrome_driver.find_element(By.XPATH, "//p/a[text()='Log In']")
    login_href.click()

    assert url == chrome_driver.current_url


def test_webapp_register_url():
    """
    GIVEN a running Heroku app
    WHEN the client clicks the Register link at the bottom of the Log In page
    THEN check the url ends with register
    """    
    chrome_driver.get('https://code-institute-ms3-book-review.herokuapp.com/login')

    url = "https://code-institute-ms3-book-review.herokuapp.com/register"

    login_href = chrome_driver.find_element(By.XPATH, "//p/a[text()='Register Your Account']")
    login_href.click()

    assert url == chrome_driver.current_url


def test_webapp_register_function():
    """
    GIVEN a running Heroku app
    WHEN the user registers
    THEN check that the user is sent to its profile page
    """    
    chrome_driver.get('https://code-institute-ms3-book-review.herokuapp.com/register')

    username = "test.user"
    password = "Passw0rd"
    message = "Congratulations, you've been registered!"

    username_element = chrome_driver.find_element(By.NAME, "username")
    password_element = chrome_driver.find_element(By.NAME, "password")
    register_button = chrome_driver.find_element(By.CLASS_NAME, "btn-primary")

    username_element.send_keys(username)
    password_element.send_keys(password)
    register_button.click()

    assert message in chrome_driver.page_source
    assert username in chrome_driver.page_source


def test_webapp_logout_function():
    """
    GIVEN a running Heroku app
    WHEN the logged in user logs out
    THEN check that the user is sent back to the login page with the message that the user has been logged out
    """    
    chrome_driver.get('https://code-institute-ms3-book-review.herokuapp.com/')

    url = "code-institute-ms3-book-review.herokuapp.com/login"
    message = "You have been successfully logged out."

    logout_href = chrome_driver.find_element(By.XPATH, "//a[text()='Log Out']")
    logout_href.click()

    assert message in chrome_driver.page_source
    assert url in chrome_driver.current_url


#  https://stackoverflow.com/questions/42142054/assert-an-element-is-not-present-python-selenium
def test_webapp_logged_out_navs():
    """
    GIVEN a running Heroku app
    WHEN the user is logged out
    THEN check that the user only sees navs for All Books, Log In and Register
    """
    chrome_driver.get('https://code-institute-ms3-book-review.herokuapp.com/')

    all_books_href = chrome_driver.find_element(By.XPATH, "//a[text()='All Books ']")
    log_in_href = chrome_driver.find_element(By.XPATH, "//a[text()='Log In']")
    register_href = chrome_driver.find_element(By.XPATH, "//a[text()='Register']")

    assert all_books_href
    assert log_in_href
    assert register_href

    with pytest.raises(Exception) as newBookExceptionInfo:
        x = chrome_driver.find_element(By.XPATH, "//a[text()='Add Book']")    
  
    with pytest.raises(Exception) as profileExceptionInfo:
        x = chrome_driver.find_element(By.XPATH, "//a[text()='Profile']")   

    with pytest.raises(Exception) as logOutExceptionInfo:
        x = chrome_driver.find_element(By.XPATH, "//a[text()='Log Out']")

# https://docs.pytest.org/en/6.2.x/assert.html
    assert 'Unable to locate element' in str(newBookExceptionInfo.value)
    assert 'Unable to locate element' in str(profileExceptionInfo.value)
    assert 'Unable to locate element' in str(logOutExceptionInfo.value)


def test_webapp_login_function():
    """
    GIVEN a running Heroku app
    WHEN the user logs in
    THEN check that the user is sent to the profile page with a flash message
    """    
    chrome_driver.get('https://code-institute-ms3-book-review.herokuapp.com/login')

    username = "test.user"
    password = "Passw0rd"
    url = "code-institute-ms3-book-review.herokuapp.com/profile/" + username
    message = "Welcome back, " + username

    username_element = chrome_driver.find_element(By.NAME, "username")
    password_element = chrome_driver.find_element(By.NAME, "password")
    login_button = chrome_driver.find_element(By.CLASS_NAME, "btn-primary")

    username_element.send_keys(username)
    password_element.send_keys(password)
    login_button.click()

    assert message in chrome_driver.page_source
    assert url in chrome_driver.current_url


def test_webapp_logged_in_navs():
    """
    GIVEN a running Heroku app
    WHEN the user is logged in
    THEN check that the user only sees navs for All Books, Add Book, Profile and Log Out
    """
    chrome_driver.get('https://code-institute-ms3-book-review.herokuapp.com/')

    all_books_href = chrome_driver.find_element(By.XPATH, "//a[text()='All Books ']")
    new_book_href = chrome_driver.find_element(By.XPATH, "//a[text()='Add Book']")
    profile_href = chrome_driver.find_element(By.XPATH, "//a[text()='Profile']")
    log_out_href = chrome_driver.find_element(By.XPATH, "//a[text()='Log Out']")

    assert all_books_href
    assert new_book_href
    assert profile_href
    assert log_out_href
   
    with pytest.raises(Exception) as logInExceptionInfo:
        x = chrome_driver.find_element(By.XPATH, "//a[text()='Log In']")   

    with pytest.raises(Exception) as registerExceptionInfo:
        x = chrome_driver.find_element(By.XPATH, "//a[text()='Register']")

    assert 'Unable to locate element' in str(logInExceptionInfo.value)
    assert 'Unable to locate element' in str(registerExceptionInfo.value)


def test_webapp_delete_profile_function():
    """
    GIVEN a running Heroku app
    WHEN the user deletes their profile
    THEN check that the user is sent to the home page with a flash message
    """
    username = "test.user"
    chrome_driver.get('https://code-institute-ms3-book-review.herokuapp.com/profile/' + username)

    url = "code-institute-ms3-book-review.herokuapp.com/get_books"
    message = "Your profile has been deleted."

    delete_profile_button = chrome_driver.find_element(By.CSS_SELECTOR, '.card-footer > .row > .col > .btn-danger')
    delete_profile_button.click()

    time.sleep(1)

    confirm_delete_button = chrome_driver.find_element(By.CSS_SELECTOR, '.modal-footer > a.btn-danger')
    confirm_delete_button.click()

    assert message in chrome_driver.page_source
    assert url in chrome_driver.current_url

    chrome_driver.close()
