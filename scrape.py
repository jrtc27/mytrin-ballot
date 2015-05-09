import getpass
from selenium import webdriver
from selenium.webdriver.support.select import Select
import sys
import urllib.parse

import room

BALLOT_URL = 'https://my.trin.cam.ac.uk/apps/accommodation/ballot_rooms_available'
BALLOT_URL_PARSED = urllib.parse.urlparse(BALLOT_URL)
MYTRIN_HOME_URL = 'https://mytrin.trin.cam.ac.uk/'
MYTRIN_HOME_URL_PARSED = urllib.parse.urlparse(MYTRIN_HOME_URL)
MYTRIN_LOGGED_OUT_URL = MYTRIN_HOME_URL
MYTRIN_LOGGED_OUT_URL_PARSED = MYTRIN_HOME_URL_PARSED
MYTRIN_LOGIN_URL = 'https://mytrin.trin.cam.ac.uk/raven/login'
MYTRIN_LOGIN_URL_PARSED = urllib.parse.urlparse(MYTRIN_LOGIN_URL)
RAVEN_AUTHENTICATE_URL = 'https://raven.cam.ac.uk/auth/authenticate.html'
RAVEN_AUTHENTICATE_URL_PARSED = urllib.parse.urlparse(RAVEN_AUTHENTICATE_URL)
RAVEN_INVALID_CREDENTIALS_URL = 'https://raven.cam.ac.uk/auth/authenticate2.html'
RAVEN_INVALID_CREDENTIALS_URL_PARSED = urllib.parse.urlparse(RAVEN_INVALID_CREDENTIALS_URL)

def get_credentials():
    username = input('Username: ')
    password = getpass.getpass('Password: ')
    return {'username': username, 'password': password}

def same_url(a, b):
    return a.scheme == b.scheme and a.netloc == b.netloc and a.port == b.port and a.path == b.path

def handle_login(driver):
    current_url_parsed = urllib.parse.urlparse(driver.current_url)
    if same_url(current_url_parsed, BALLOT_URL_PARSED):
        # No need to log in
        return

    # Ensure we are in fact logged out
    assert same_url(current_url_parsed, MYTRIN_LOGGED_OUT_URL_PARSED), current_url_parsed

    # Go to the login page
    driver.get(MYTRIN_LOGIN_URL)
    current_url_parsed = urllib.parse.urlparse(driver.current_url)

    # Check we were redirected to Raven - don't want to enter credentials on another page
    assert same_url(current_url_parsed, RAVEN_AUTHENTICATE_URL_PARSED), current_url_parsed

    credentials = get_credentials()

    # Fill in credentials
    form = driver.find_element_by_name('credentials')
    userid_field = form.find_element_by_name('userid')
    password_field = form.find_element_by_name('pwd')
    userid_field.send_keys(credentials['username'])
    password_field.send_keys(credentials['password'])
    form.submit()

    current_url_parsed = urllib.parse.urlparse(driver.current_url)
    # Check we weren't redirected to the login error page
    if same_url(current_url_parsed, RAVEN_INVALID_CREDENTIALS_URL_PARSED):
        print("Wrong username/password", file=sys.stderr)
        sys.exit(1)

    # If not, make sure we were actually logged in to MyTrin
    assert same_url(current_url_parsed, MYTRIN_HOME_URL_PARSED)

    # Now retry going to the ballot application
    driver.get(BALLOT_URL)
    current_url_parsed = urllib.parse.urlparse(driver.current_url)
    assert same_url(current_url_parsed, BALLOT_URL_PARSED)

def get_table(driver):
    form = driver.find_element_by_id('frm_1')
    select = Select(driver.find_element_by_id('sel_court'))
    select.select_by_value('-1') # -1 means all
    # Has no name nor id - have to resort to the fact that it is the only
    # table-like table and thus use a CSS selector
    return driver.find_element_by_css_selector('table.standard_table')

def extract_data(table):
    def tr_get_tds(tr):
        tds = tr.find_elements_by_tag_name('td')
        # 9 columns
        assert len(tds) == 9
        return tds
    body = table.find_element_by_tag_name('tbody')
    rows = body.find_elements_by_tag_name('tr')
    # Discard header
    rows = rows[1:]
    l = len(rows)
    assert l > 0
    for i in range(l):
        rows[i] = room.Room(tr_get_tds(rows[i]))
        print(str(rows[i]), end=' ', file=sys.stderr)
        rows[i].download_to_file()
        print('{} / {}'.format(i+1, l), file=sys.stderr)
    return rows

def get_rooms():
    driver = webdriver.PhantomJS()
    driver.implicitly_wait(10)

    driver.get(BALLOT_URL)

    handle_login(driver)

    table = get_table(driver)
    data = extract_data(table)

    driver.quit()

    return data

def scrape():
    rooms = get_rooms()
    room.save_to_json(rooms)
    return rooms
