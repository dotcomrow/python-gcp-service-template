from flask import Response
import json
from google.oauth2 import service_account
import multiprocessing
from googleapiclient.discovery import build
import time
                           
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user',
          'https://www.googleapis.com/auth/admin.directory.group']

def list_all_groups_a_user_is_a_part_of(sid, app, return_dict):
    """
    This method will list all the groups a user is a part of and return them as a list
    """
    listOfEmailGroups=[]
    credentials = service_account.Credentials.from_service_account_file(
                                '/secrets/google.key', 
                                scopes=SCOPES)
    service = build('admin', 'directory_v1', credentials=credentials)
    results = service.groups().list(domain=app.config['DOMAIN'],userKey=sid, maxResults=400).execute()
    groups = results.get('groups', [])
        
    for group in groups:
        listOfEmailGroups.append({
            'group_email': group['email'],
            'group_name': group['name']
        })
    return_dict['groups'] = listOfEmailGroups

def handle_get(user, app):
    result = {}
    processing_group = []
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    processing_group.append(multiprocessing.Process(target=list_all_groups_a_user_is_a_part_of, args=(user['sub'], app, return_dict,)))
    for p in processing_group:
        p.start()

    starttime = time.time()
    while time.time() - starttime < 30:
        if not any(p.is_alive() for p in processing_group):
            break
        time.sleep(.1)

    for p in processing_group:  
        p.join(30)
        if p.is_alive():
            p.join()
            exit(1)
    
    for return_key in return_dict.keys():
        result[return_key] = return_dict[return_key]
        
    return Response(response=json.dumps(result), status=200, mimetype="application/json")
