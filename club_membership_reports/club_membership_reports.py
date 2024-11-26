'''
This script is purpose built for an organization that needs to export their membership data out of the
Paid Memberships Pro plugin in Wordpress, divide the data up per club into individual Excel spreadsheets,
and then save them to each club's Google Drive folder.

config.yaml, client_secrects.json, and gdrive_auth.txt files are prerequisites. See the example files for details.
Logs are saved to ./output.log
'''

import pandas as pd
import yaml
import os
import io
import logging
import requests
from urllib3.util import Retry
from openpyxl import load_workbook
from openpyxl.worksheet.table import Table
from openpyxl.utils import get_column_letter
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def create_logger():
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('output.log', mode='w')
    handler.setFormatter(formatter)
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    log.addHandler(handler)

    return log

def load_config(filepath):
    # Load config.yaml file
    try:
        with open(filepath, 'r') as file:
            return yaml.safe_load(file)
    except:
        logger.exception('failed to load config.yaml')

def get_membership_data(config):
    header = config['wordpress']['header']
    wp_login = config['wordpress']['wp_login']
    wp_admin = config['wordpress']['wp_admin']
    username = config['wordpress']['username']
    password = config['wordpress']['password']
    csv_url = config['wordpress']['csv_url']
    login_data = {
        'log':username, 
        'pwd':password, 
        'wp-submit':'Log In', 
        'redirect_to':wp_admin, 
        "rememberme": "forever", 
        'testcookie':'1' 
    }
    retry = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[408, 429, 500, 502, 503, 504],
    )

    # Build HTTP Client
    adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    client = requests.Session()
    client.headers.update(header)
    client.mount('https://', adapter)

    # Authenticate with Wordpress server
    try:
        login = client.post(wp_login, data=login_data, timeout=180)
        if login.ok:
            logger.info('successfully logged into Wordpress')
    except:
        logger.exception(f'failed to authenticate with Wordpress server')
        client.close()
        os._exit(0)
    
    # Download the membership CSV file from the Paid Membership Pro plugin
    try:
        response = client.post(csv_url, allow_redirects=True, timeout=180)
        if response.ok:
            logger.info('successfully downloaded membership CSV file')
    except:
        logger.exception(f'failed to download csv file')
        client.close()
        os._exit(0)

    # Close the connection
    client.close()

    try:
        raw_data = response.content.decode('utf8')
    except:
        logger.exception(f'failed to decode CSV data')
    
    try:
        data = pd.read_csv(io.StringIO(raw_data))
        logger.info(f'{len(data)} members found in data')
    except:
        logger.exception(f'failed to create Pandas dataframe from CSV data')

    # Get unique club names from membership list
    try:
        club_list = set(data['home_club'])
        logger.info(f'{len(club_list)} clubs found in data')
    except:
        logger.exception('failed to get club list from csv data')

    return data, club_list

def create_club_spreadsheets(data, club_list):
    # Filter for rows where the column 'home_club' matches the the club name
    for club in club_list:
        # Filter out 'unknown' home_club
        if 'unknown' not in club.lower():
            # Save to Excel
            filename = f'{club}.xlsx'
            club_data = data[data['home_club'] == club]

            # Write the data to an Excel file
            try:
                club_data.to_excel(filename, sheet_name="members", index=False)
            except:
                logger.exception(f'failed to export {club} spreadsheet to Excel file')

            # Load the recently created excel spreadsheet
            wb = load_workbook(filename)
            ws = wb["members"]

            # Remove unneeded columns. In this case: columns G-M
            ws.delete_cols(7, 7)

            # Format the spreadsheet as a table
            table = Table(displayName="Table1", ref="A1:" + get_column_letter(ws.max_column) + str(ws.max_row))
            ws.add_table(table)

            # Autofit column width  
            for column in ws.columns:
                max_length = 0
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = max_length + 6
                ws.column_dimensions[column[0].column_letter].width = adjusted_width

            # Save changes
            wb.save(filename)

def gauth_client():
    gauth = GoogleAuth()

    # Load saved client credentials (does not exist when running this for the first time)
    gauth.LoadCredentialsFile("gdrive_auth.txt")

    if gauth.credentials is None:
        # Authenticate with Google Drive if credentials are missing
        gauth.settings.update({'get_refresh_token': True})

        try:
            gauth.LocalWebserverAuth()
            logger.info('authenticated with Google Cloud API')
        except:
            logger.exception('failed to authenticate with Google Cloud API')

    elif gauth.access_token_expired:

        try:
            gauth.Refresh()
            logger.info('refreshed the Google Cloud API token')
        except:
            logger.exception('failed to refresh the Google Cloud API token')
    else:

        try:
            gauth.Authorize()
            logger.info('loaded the cached Google Cloud API token')
        except:
            logger.exception('failed to load the cached Google Cloud API token')

    # Save the current credentials to file for the next time the script is ran
    try:
        gauth.SaveCredentialsFile("gdrive_auth.txt")
    except:
        logger.exception('failed to save gdrive credentials file')

    return GoogleDrive(gauth)

def gdrive_upload(gclient, club_list, config):
    #Get Google Drive folder IDs for each club folder
    try:
        folder_list = gclient.ListFile({'q': f"'{config['google_drive']['gdrive_id']}' in parents and trashed=false"}).GetList()
    except:
        logger.exception('failed to get list of club folders from Google Drive')

    for club in club_list:
        if 'unknown' not in club.lower():
            logger.info(f'club name: {club}')
            club_folder_id = ''
            for club_folder in folder_list:
                if club_folder['title'] == club:
                    club_folder_id = club_folder['id']
                    logger.info(f'club folder id: {club_folder_id}')
                    break
                
            if club_folder_id == None:
                logger.info('no club folder found. Creating...')

                # Create the club folder
                folder_metadata = {
                    'title': club,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [{'id': config['gdrive_id']}]
                }
                folder = gclient.CreateFile(folder_metadata)

                try:
                    folder.Upload()
                    logger.info(f'{club} folder successfully created')
                except:
                    logger.exception(f'failed to create {club} folder on Google Drive')

                club_folder_id = folder['id']
                logger.info(f'club folder id: {club_folder_id}')

            # Get a list of files within the club's Google Drive folder
            try:
                file_list = gclient.ListFile({'q': f"'{club_folder_id}' in parents and trashed=false"}).GetList()
            except:
                logger.exception('failed to get list of club files from Google Drive')

            # Get existing file ID if present so that we can overwrite the old spreadsheet with the new one
            filename = f'{club}.xlsx'
            gfile_id = ''
            
            for gfile in file_list:
                if gfile['title'] == filename:
                    gfile_id = gfile['id']
                    logger.info(f'club spreadsheet id: {gfile_id}')
                    break
                
            if gfile_id:
                file_metadata = {
                    'title': filename,
                    'id': gfile_id,
                    'parents': [{'id': club_folder_id}]
                }
            else:
                logger.info(f'no club spreadsheet found. Creating...')

                # Leave ID out of the metadata so that a new file is created
                file_metadata = {
                    'title': filename,
                    'parents': [{'id': club_folder_id}]
                }

            # Upload the Excel file to Google Drive 
            file = gclient.CreateFile(file_metadata)
            file.SetContentFile(filename)
            try:
                file.Upload()
                logger.info(f'{filename} successfully uploaded')
            except:
                logger.exception(f'failed to create {filename} on Google Drive')

            # Clean up local copy of the club members spreadsheet
            os.remove(filename)

def main():
    global logger 
    logger = create_logger()
    config = load_config('config.yaml')
    csv_data, club_list = get_membership_data(config)
    create_club_spreadsheets(csv_data, club_list)
    gclient = gauth_client()
    gdrive_upload(gclient, club_list, config)

if __name__ == "__main__":
    main()
