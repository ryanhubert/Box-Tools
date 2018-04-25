#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Ryan Hübert
# Department of Political Science
# University of California, Davis

# Website: https://www.ryanhubert.com/

"""
Tools for Box API
"""

import os
import re
import keyring
from boxsdk import Client, OAuth2
from getpass import getpass

def BoxAuth(box_user_name, suppress_warnings=False):
    if suppress_warnings == False:
        warn = input(
                "WARNING: This module accesses and stores info \n"
                "         in your local keychain using keyring module.\n\n"
                "Do you want to proceed? [y/n] "
                )
    else:
        warn = 'y'

    if warn in ["y", "yes", "Yes", "YES"]:

        # Define client ID and client secret
        if keyring.get_password('box_python_sdk_client_id', box_user_name) == None:
            print("You need to have a Box Developer account to do this.\n" + 
                  "Follow instructions available at \n" + 
                  "github.com/ryanhubert/Box-Tools/blob/master/README.md"
                  )
            CID = getpass('Paste Client ID Here: ')
            CSC = getpass('Paste Client Secret Here: ')
            keyring.set_password('box_python_sdk_client_id', box_user_name, CID)
            keyring.set_password('box_python_sdk_client_secret', box_user_name, CSC)
            del CID, CSC
            
        def read_tokens():
            """Reads authorization tokens from system keychain"""
            auth_token = keyring.get_password('box_python_sdk_auth', box_user_name)
            refresh_token = keyring.get_password('box_python_sdk_refr', box_user_name)
            return (auth_token, refresh_token)

        def store_tokens(access_token, refresh_token):
            """Callback function when Box SDK refreshes tokens"""
            # Use keyring to store the tokens
            keyring.set_password('box_python_sdk_auth', box_user_name, access_token)
            keyring.set_password('box_python_sdk_refr', box_user_name, refresh_token)

        # Authenticate with stored tokens
        access_token, refresh_token = read_tokens()

        if access_token != None:
            # Set up authorisation using the tokens we've retrieved
            oauth = OAuth2(
                client_id=keyring.get_password('box_python_sdk_client_id', box_user_name),
                client_secret=keyring.get_password('box_python_sdk_client_secret', box_user_name),
                access_token=access_token,
                refresh_token=refresh_token,
                store_tokens=store_tokens,
            )

        else:
            # Authenticate for first time and store tokens
            oauth = OAuth2(
                client_id=keyring.get_password('box_python_sdk_client_id', box_user_name),
                client_secret=keyring.get_password('box_python_sdk_client_secret', box_user_name),
                store_tokens=store_tokens,
            )
            print("To authorize access to your Box account please do the following:\n\n" +
                  "1. Navigate to the following URL in a browser:\n")
            print(oauth.get_authorization_url('http://localhost')[0])
            print("\n2. Select 'Grant Access to Box'.\n")
            print(
                "3. Extract the access code from the resulting URL (in your browser's address bar, the string after 'code=').\n")
            boxcode = input("4. Paste it here: ")
            access_token, refresh_token = oauth.authenticate(boxcode)
            keyring.set_password('box_python_sdk_auth', box_user_name, access_token)
            keyring.set_password('box_python_sdk_refr', box_user_name, refresh_token)

            # Create the SDK client
        client = Client(oauth)

        # Get information about the logged in user (that's whoever owns the developer token)
        # current_user = client.user(user_id='me').get()
        # print("You are now logged into Box as: " + current_user.name + ' (' + current_user.login + ')')
        
        return client

    else:
        print("\nBox authentication failed!\n")
        return None

def BoxCreateFolderScheme(path,box_user_id,box_root_dir='0',suppress_warnings=False):
    #path = '/TEST1/TEST2/TEST3/TEST4/'
    client = BoxAuth(box_user_id,suppress_warnings=True)
    NewFolder = client.folder(box_root_dir)
    for i in [x for x in path.split('/') if not x in ['',' ']]:
        NewFolder = NewFolder.create_subfolder(i)

def BoxFolderUpload(box_folder_id, local_path, box_user_id, 
                    suppress_warnings=False, overwrite=False):
    """
    Takes Box folder (ID number as string) and local path (as string)
    and saves all contents of local directory into the Box folder.
    """
    
    if overwrite == False:
        print("WARNING:\n" + 
              "   This will NOT upload any local file if Box\n" + 
              "   folder contains a file with the same name.\n"
              "   It will just skip them!")
    
    local_path = re.sub('/ *$','',local_path)
    
    # Connect to Box
    client = BoxAuth(box_user_id,suppress_warnings)
    RootFolder = client.folder(box_folder_id)
    
    if re.search('\.[A-z0-9]+$',local_path):
        """
        this is a file
        """
        filename = re.search('/([^/]+\.[A-z0-9]+)$',local_path).group(1)
        try:
            RootFolder.upload(local_path, filename)
            print("File loaded to Box!")
        except Exception as e:
            if overwrite == True and 'Code: item_name_in_use' in str(e):
                file_to_delete = re.search("'id': '(\d+)'",str(e)).group(1)
                client.file(file_to_delete).update_contents(local_path)
                print("File loaded to Box!")
            else:
                print("Did not save to Box due to following error:")
                print(str(e))
                raise
    
    else:   
        """
        this is a folder
        """
        dirname = re.search('/([^/]+)/?$',local_path).group(1)
        current_folder_files = [x for x in os.walk(local_path)][0][2]
        current_folder_files = [x for x in current_folder_files if not re.search('^\.',x)]
        try:
            DataFolder = RootFolder.create_subfolder(dirname)
        except Exception as e:
            DataFolder = client.folder(re.search("'id': '(\d+)'",str(e)).group(1))
        print("Loading files to Box folder " + dirname, end=" ")
        for j in current_folder_files:
            print('.', end='')
            filepath = local_path + '/' + j
            try:
                DataFolder.upload(filepath, j)
            except Exception as e:
                if overwrite == True and 'Code: item_name_in_use' in str(e):
                    file_to_delete = re.search("'id': '(\d+)'",str(e)).group(1)
                    client.file(file_to_delete).update_contents(filepath)
                elif overwrite == False and 'Code: item_name_in_use' in str(e):
                    pass
                else:
                    print("\n\nStopped saving to Box due to following error:")
                    print(str(e))
                    raise
        print(" all files loaded to Box!")