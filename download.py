# coding=utf-8
from __future__ import print_function

import datetime
import os
import sys
import tempfile
import time
from shutil import copyfile

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

import click

TARGET_DATA_FOLDER = '/data'
PAGE_TRANSITION_WAIT = 120  # seconds
DOWNLOAD_TIMEOUT = 20  # seconds


def eprint(*args, **kwargs):
    print("[ERROR]", *args, file=sys.stderr, **kwargs)

def iprint(*args, **kwargs):
    print("[INFO]", *args, **kwargs)
    sys.stdout.flush()

def init_chrome(download_folder):
    iprint("Starting chrome...")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_experimental_option('prefs', {
        'download.default_directory': download_folder,
        'download.prompt_for_download': False,
        'directory_upgrade': True
    })

    d = webdriver.Chrome(chrome_options=chrome_options)
    d.implicitly_wait(PAGE_TRANSITION_WAIT)

    enable_download_in_headless_chrome(d, download_folder)
    return d

def enable_download_in_headless_chrome(driver, download_dir):
    """
    there is currently a "feature" in chrome where
    headless does not allow file download: https://bugs.chromium.org/p/chromium/issues/detail?id=696481
    This method is a hacky work-around until the official chromedriver support for this.
    Requires chrome version 62.0.3196.0 or above.
    """

    # add missing support for chrome "send_command"  to selenium webdriver
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    command_result = driver.execute("send_command", params)
    print("response from browser:")
    for key in command_result:
        print("result:" + key + ":" + str(command_result[key]))

def quit_chrome(d):
    iprint("Closing chrome")
    d.quit()


def click_on(d, xpath):
    iprint("Waiting for " + xpath)
    WebDriverWait(d, PAGE_TRANSITION_WAIT).until(
        EC.element_to_be_clickable((By.XPATH, xpath)))
    iprint("Clicking " + xpath)
    d.find_element_by_xpath(xpath).click()


def wait_for_download(dirname):
    iprint("Waiting for download to finish (by checking the download folder)")
    waiting_time = 0
    sleep_interval = 0.1
    def is_downloaded():
        return os.listdir(dirname) and os.listdir(dirname)[0].endswith(".TAB")
    while waiting_time < DOWNLOAD_TIMEOUT and not is_downloaded():
        time.sleep(sleep_interval)
        waiting_time += sleep_interval

    if waiting_time >= DOWNLOAD_TIMEOUT:
        eprint("Something went wrong, file download timed out")
        sys.exit(1)


def download_with_chrome(
        account_number, card_number, identification_code,
        period_from, period_to):

    download_folder = tempfile.mkdtemp()
    d = init_chrome(download_folder)
    try:
        iprint("Loading login page")
        d.get("https://www.abnamro.nl/portalserver/my-abnamro/my-overview/overview/index.html")

        iprint("Accepting cookies")
        try:
            click_on(d, "//*[text()='Yes, I accept cookies']")
        except TimeoutException:
            iprint("Cookies window didn't pop up")

        iprint("Accepting menu changes")
        try:
            click_on(d, "//*[text()='Continue']")
        except TimeoutException:
            iprint("menu change window didn't pop up")

        # iprint("Accepting IBAN changes")
        # try:
        #     click_on(d, "//*[text()='Continue']")
        # except TimeoutException:
        #     iprint("IBAN window didn't pop up")

        iprint("Logging in")
        # click_on(d, "//*[@title='Log in to Internet Banking']")
        # click_on(d, "//*[@title='Log on with your identification code']/span")

        element = d.find_element_by_xpath("//*[(@label='Identification code')]")
        element.click()

        d.find_element_by_name('accountNumber').send_keys(account_number)
        d.find_element_by_name('cardNumber').send_keys(card_number)
        d.find_element_by_name('inputElement').send_keys(identification_code)
        d.find_element_by_id('login-submit').click()
        # click_on(d, "//button[@type='submit']")

        iprint("We are in, navigation to the export page")
        # try:
        #     click_on(d, "//*[text()='Yes, I accept cookies']")
        # except TimeoutException:
        #     iprint("Cookies window didn't pop up")

        click_on(d, "//*[text()='Self service']")
        click_on(d, "//*[text()=' Download transactions ']")

        iprint("Filling in export parameters")
        # Below section commented out to download transactions since last download
        # def fill_datepart(name, value):
        #     elem = d.find_element_by_name('mutationsDownloadSelectionCriteriaDTO.' + name)
        #     elem.clear()
        #     elem.send_keys(value)

        # fill_datepart('bookDateFromDay', period_from.strftime('%d'))
        # fill_datepart('bookDateFromMonth', period_from.strftime('%m'))
        # fill_datepart('bookDateFromYear', period_from.strftime('%Y'))
        # fill_datepart('bookDateToDay',  period_to.strftime('%d'))
        # fill_datepart('bookDateToMonth', period_to.strftime('%m'))
        # fill_datepart('bookDateToYear', period_to.strftime('%Y'))
        # click_on(d, "//label[@for='periodType1']")

        options = Select(d.find_element_by_xpath('//form/section[1]/fieldset/select'))
        options.select_by_visible_text('TXT')

        time.sleep(1)  # just to be sure, a lot of heavy JS is going on there
        iprint("Clicking OK to download file")
        click_on(d, "//*[text()='download']")

        wait_for_download(download_folder)

        iprint("Copying downloaded file to the target directory")
        downloaded_filename = os.listdir(download_folder)[0]
        src_file = os.path.join(download_folder, downloaded_filename)
        dst_file = os.path.join(TARGET_DATA_FOLDER,  downloaded_filename)
        copyfile(src_file, dst_file)
        iprint("Done! Transaction file is located at " + dst_file)
        return dst_file

    except:
        quit_chrome(d)
        raise

    quit_chrome(d)

def get_env_var(name):
    if name in os.environ:
        return os.environ[name]
    else:
        eprint("Environmental variable " + name + " not found")
        sys.exit(1)

def parse_date(s):
    try:
        return datetime.datetime.strptime(s, '%Y-%m-%d')
    except ValueError:
        eprint(s, "is not a date in YYYY-MM-DD format")
        sys.exit(1)

@click.command()
@click.option('--period-from', help='Date from, format YYYY-MM-DD', required=False)
@click.option('--period-to', help='Date to, format YYYY-MM-DD', required=False)
@click.option('--export-filename', help='Name of the downloaded CSV file')
def run(period_from, period_to, export_filename):
    """Download a list of transactions from AirBank"""
    download_with_chrome(
        account_number=get_env_var("ABNAMRO_ACCOUNT_NUMBER"),
        card_number=get_env_var("ABNAMRO_CARD_NUMBER"),
        identification_code=get_env_var("ABNAMRO_IDENTIFICATION_CODE"),
        period_from=parse_date(period_from),
        period_to=parse_date(period_to)
    )

if __name__ == '__main__':
    run()
