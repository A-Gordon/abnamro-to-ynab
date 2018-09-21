#!/usr/bin/env python
import csv
import datetime
import os
import subprocess
import sys

import download

env_file = "/data/.env_vars"
downloader = "/src/downloader/download.py"
converter = "/src/converter/convert.py"
# converter = "./converter/convert.py"
TARGET_DATA_FOLDER = '/data'
archived_data_folder = TARGET_DATA_FOLDER + "/archived"

period_from = '2018-05-01'
period_to = '2018-05-14'

def get_env_var(name):
    if name in os.environ:
        return os.environ[name]
    else:
        print("Environmental variable " + name + " not found")
        sys.exit(1)

def create_env_file(_file):
    account_number=get_env_var("ABNAMRO_ACCOUNT_NUMBER")
    card_number=get_env_var("ABNAMRO_CARD_NUMBER")
    identification_code=get_env_var("ABNAMRO_IDENTIFICATION_CODE")
    ynab_access_token=get_env_var("YNAB_ACCESS_TOKEN")
    ynab_budget_id=get_env_var("YNAB_BUDGET_ID")
    ynab_account_id=get_env_var("YNAB_ACCOUNT_ID")

    file = open(_file, "w")
    file.write("export ABNAMRO_ACCOUNT_NUMBER=" + account_number )
    file.write("\nexport ABNAMRO_CARD_NUMBER=" + card_number )
    file.write("\nexport ABNAMRO_IDENTIFICATION_CODE=" + identification_code )
    file.write("\nexport YNAB_ACCESS_TOKEN=" + ynab_access_token )
    file.write("\nexport YNAB_BUDGET_ID=" + ynab_budget_id )
    file.write("\nexport YNAB_ACCOUNT_ID=" + ynab_account_id )
    file.write ("\n")

def downloading():

    downloaded_data_file = download.download_with_chrome(
        account_number=get_env_var("ABNAMRO_ACCOUNT_NUMBER"),
        card_number=get_env_var("ABNAMRO_CARD_NUMBER"),
        identification_code=get_env_var("ABNAMRO_IDENTIFICATION_CODE"),
        period_from=period_from,
        period_to=period_to
    )
    return downloaded_data_file

def converttocsv(_file):
    
    absolute_path = os.path.abspath(_file)
    path, filename = os.path.split(absolute_path)
    filename_only = os.path.splitext(filename)[0]
    newfilename = '%s.csv' % filename_only
    csv = os.path.join(path, newfilename)
    
    print "Converting %s now" % absolute_path
    _cmd = 'python ' + converter + " " + absolute_path + ' > ' + csv

    print (_cmd)
    result = execute(_cmd)

    sed_cmd = "sed -i '/,\^/ {d; }' " + csv
    sed_result = execute(sed_cmd)

    archive_files(_file)

    return csv

def execute(command):

    pipe = subprocess.Popen(command, shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = pipe.communicate()
    result = out.decode()
    print (result)
    return result

def fintech(_csv_file):
    
    ynab_account_id=get_env_var("YNAB_ACCOUNT_ID")

    _cmd = 'cd /src/fintech-to-ynab; rails runner "Import::Csv.new(\'%s\', \'%s\').import"' % (_csv_file, ynab_account_id)
    print (_cmd)
    result = execute(_cmd)
    archive_files(_csv_file)

def archive_files(_file):

    absolute_path = os.path.abspath(_file)
    path, filename = os.path.split(absolute_path)
    print path
    print filename
    archived_file = path + "/archived/" + filename
    print archived_file
    os.rename(_file, archived_file)

if __name__ == '__main__':
    create_env_file(env_file)
    raw_file = downloading()
    csv_file = converttocsv(raw_file)
    fintech(csv_file)
