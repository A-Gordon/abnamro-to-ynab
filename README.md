# AbnAmro-to-YNAB
This is an amalgamation of multiple projects. 

These are 
- abnamro-tx: Took out the dates and simply download since the last statement download
- abncsv2qif: Took out the memo section to fit with csv upload in bulk with fintech-to-ynab
- fintech-to-ynab: Used to import the csv

## Function
The aim of this project is to combine the three above into a single functioning auto import feature for abn amro to ynab.

Currently the resulting container will run a python script that uses selenium to log into the ABN AMRO web portal, download a transactions statement and convert that into a csv. Once converted it will run fintech-to-ynab to upload the csv to the ynab account. 

It is currently configured to run this every 15 mins by invoking cron. 


## Getting Started
- Clone the repo
- Build the container
- Run

### Build
```docker build -t {{container_name}} .```

### Run
Run with privilege, a path mapped to /data and the required variables passed through. These can passed using the -e flag or --env-file to pass them in a file.

`docker run --env-file=../env.list --volume $(pwd)/export-data:/data --privileged {{container_name}}:latest`

These are : 
- ABNAMRO_ACCOUNT_NUMBER
- ABNAMRO_CARD_NUMBER
- ABNAMRO_IDENTIFICATION_CODE
- YNAB_ACCESS_TOKEN
- YNAB_BUDGET_ID
- YNAB_ACCOUNT_ID


If you want to test this without the cronjob then change the entrypoint/cmd to /src/updater.sh

## To do 
- Add different directory structure
- Add actual logging, currently just outputs ugly logs to stdout
- Tidy up and restructure code

> This app is not officially supported by YNAB in any way. Use of this app could introduce problems into your budget that YNAB, through its official support channels, will not be able to troubleshoot or fix. Please use at your own risk!