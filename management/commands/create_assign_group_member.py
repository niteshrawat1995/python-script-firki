__author__ = 'Kritika Arora'
import random
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from datetime import datetime
from random import randint
import requests
import csv
import os
import json

discussion_url = settings.FEATURES['DISCUSSION_URL']
api_key = settings.FEATURES['discussion_api_key']
api_username=settings.FEATURES['DISCUSSION_API_USER']
querystring = {"api_key": api_key, "api_username": api_username}
usercreateurl = discussion_url + "users.json"

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

#BASE_DIR = settings.BASE_DIR # /edx-platform/

# FILE_PATH = os.path.join(BASE_DIR, "docs", "class_6", "Class_6.csv")


#CSV_PATH = os.path.join(BASE_DIR, "lms/djangoapps/mx_discourse/management/commands/csv2020", "AP Teachers 08.csv")

def logger(file_name, success_list):
    with open("lms/djangoapps/mx_discourse/user_created.txt", "a") as f:
        f.write(file_name + "\t" + str(datetime.now()) + "\n")
        for email in success_list:
            f.write(email + "\n")


def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


def getOrCreateGroup(group_name):
    group_name = group_name.strip().replace(" ", "-")
    get_groups_url = discussion_url + "/groups/" + group_name + ".json"
    response = requests.request("GET", get_groups_url, params=querystring)
    if response.status_code == 200:
        try:
            return response.json()["basic_group"]
        except KeyError:
            return response.json()["group"]
    else:
        logging.info("group don't exit")
        return None
        # creating the group in the discourse
        # payload = {
        #     "group[name]": group_name
        # }
        # response = requests.request("POST", discussion_url + "admin/groups.json", data=payload, params=querystring)
        # if response.status_code != 200:
        #     print(response.text)
        # else:
        #     try:
        #         return response.json()["basic_group"]
        #     except KeyError:
        #         return response.json()["group"]



def addMembersAndOwners(group_info, members, owners):

    members = ",".join(members)
    owners = ",".join(owners)
    if owners != "":
        owners_data = {
            "group[usernames]": owners
        }

        url = discussion_url + "admin/groups/" + str(group_info["id"]) + "/owners.json"
        res = requests.request("PUT", url=url, data=owners_data, params=querystring)
        if res.status_code != 200:
            print(res.text)
        else:
            print("owners added=>", owners_data)

    if members != "":
        members_data = {
            "usernames": members
        }

        url = discussion_url + "admin/groups/" + str(group_info["id"]) + "/members.json"
        res = requests.request("PUT", url=url, data=members_data, params=querystring)
        if res.status_code != 200:
            print(res.text)
        else:
            print("members added=>", members_data)

def discourse_user_exists(username):
    api_url='{}/users/{}.json'.format(discussion_url,username)
    try:
        response = requests.request("GET", api_url, params=querystring)
        if response:
            return True
        else:
            logging.info('discourse user get error:{}'.format(username))
            return False
    except Exception as e:
        logging.info('discourse user get error:{}'.format(username))
        return False

def create_discourse_user(edx_user):

    password = edx_user.username + ''.join(
        random.choice('0123456789ABCDEF') for i in range(3))
    payload = {
        "name": edx_user.first_name ,
        "email": edx_user.email.strip(),
        "password": password,
        "username": edx_user.username.strip(),
        "active": True,
        "trust_level": 1
    }
    response = requests.request("POST", usercreateurl, data=payload, params=querystring)

    res_mess = json.loads(response._content)
    error_mess = res_mess["message"]

    if res_mess['message'] == 'Primary email has already been taken':
        email = str(random_with_N_digits(4))+"_"+edx_user.email.strip()
        payload = {
            "name": edx_user.first_name ,
            "email": email,
            "password": password,
            "username": edx_user.username.strip(),
            "active": True,
            "trust_level": 1
        }
        response = requests.request("POST", usercreateurl, data=payload, params=querystring)

    if response.status_code == 200:
        return True 
    else:
        logging.info(response.text)
        return False

def get_or_create_edx_user(row):
    csv_username=row['username'].strip()
    csv_email=row['email'].strip()
    
    if '@' in csv_username:
        csv_username = csv_username.split("@")[0]
    try:
        #check and return if found user using its email id
        edx_user=User.objects.get(email__iexact=csv_email)
        return edx_user
    except User.DoesNotExist as e:
        logging.info("{} not exist.".format(csv_email))

    try:
        # first_name, last_name = row['name'].strip().split(" ")
        first_name = row['name'].strip().split(" ")[:-1]
        first_name = ' '.join(first_name)
        last_name = row['name'].strip().split(" ")[-1]
    except ValueError as e:
        first_name = row['name'].strip().split(" ")[0]
        last_name = ""
        print(e)
    try:
        User.objects.get(username__iexact=csv_username)
        # if csv email and username not in edx
        csv_username = csv_username+'_'+str(random_with_N_digits(4))
        edx_user=User(username=csv_username,
            email=csv_email,
            password=make_password(csv_email.split("@")[0] + "@123"),
            first_name=first_name,
            last_name=last_name,
            is_active=True)
        edx_user.save()
        logging.info('User register in edx with email: '+csv_email+ 'username : '+ csv_username)
        return edx_user
    except User.DoesNotExist as e:
        edx_user=User(username=csv_username,
            email=csv_email,
            password=make_password(csv_email.split("@")[0] + "@123"),
            first_name=first_name,
            last_name=last_name,
            is_active=True)
        edx_user.save() 
        logging.info('User register in edx with email: '+csv_email+ 'username : '+ csv_username)
        return edx_user
    

# def rename_usernames(old_username,new_username):
#     endpoint="{}u/{}/preferences/username.json".format(discussion_url,old_username)
    
#     payload = {'new_username':new_username}
#     headers={"Content-Type": "multipart/form-data"}
#     r = requests.put(endpoint, data=payload,headers=headers,params=querystring)
#     if r:
#         print('sucess')
#     else:
#         print('failure')


def validate_or_create_discourse_user(row,edx_user):
    is_discourseuser=discourse_user_exists(edx_user.username)
    if is_discourseuser:
        return True

    created=create_discourse_user(edx_user)
    if created:
        return True 
    else: 
        return False
    

       
    
class Command(BaseCommand):
    """
    This command will add users(from csv) to discourse (that are not in discourse earlier)
    """
    args = ''
    help = 'Used to migrate user from edx to discourse'

    def add_arguments(self, parser):
        parser.add_argument('csv_path')

    def handle(self, *args, **options):
        '''
          Operation: to assign user to discourse groups of discourse
          Input: file path
          Output: None
          Developer : 'Kritika Arora'
          Date: 7/September/2019
        '''
        print("===> Operation Start ===>")
        # import ptvsd
        # ptvsd.wait_for_attach()
        csv_path = options["csv_path"]#CSV_PATH
        file_name = csv_path.split("/")[-1]
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            owners = []
            members = []
            success_list=[]
            for row in reader:
                print('---------------------------------New Row------------------------------------')
                csv_username=row['username'].strip()
                csv_email=row['email'].strip()
                # if csv_username=='shreejita.s2018@teachforindia.org':
                #     import pudb; pudb.set_trace()
                try:
                    edx_user=get_or_create_edx_user(row)
                except Exception as e:
                    logging.info("{} edx user is not created".format(csv_email))
                    logging.error(e)
                    continue
                    
                is_user_created=validate_or_create_discourse_user(row,edx_user)
                if not is_user_created:
                    continue

                success_list.append(csv_email)
               
                # if user is not owners then save it in members list
                if row['owner'] and row['owner'].lower() == 'owner':
                    owners.append(edx_user.username)
                # if user is owners then save it in owners list
                else:
                    members.append(edx_user.username)

            logger(file_name, success_list)
            group_details = getOrCreateGroup(row['group_name'])
            if group_details:
                addMembersAndOwners(group_details, members, owners)

        print("===> Operation End ===>")
