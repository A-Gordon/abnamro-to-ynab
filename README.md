This is an amalgamation of multiple projects

These are 
abnamro-tx: Took out the dates and simply download since the last statement download
abncsv2qif: Took out the memo section to fit with csv upload in bulk by fintech sed -i.bak '/\^/ { N; d; }' test.csv
fintech-to-ynab: Used to import the csv

The aim of this project is to combine the three above into a single functioning auto import feature for abn amro to ynab

TARGET_DATA_FOLDER = './data'


To do 
Cron
Add fucntionality to download a date range
Add more functionality around headless/windows
tidy up directories
code it properly
Add actual logging


docker run --env-file=../env.list --volume $(pwd)/export-data:/data --privileged ag_testing:latest

xvfb-daemon-run python download.py --period-from "2018-05-01" --period-to "2018-05-14"
