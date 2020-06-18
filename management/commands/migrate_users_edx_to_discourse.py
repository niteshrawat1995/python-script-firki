__author__ = 'Avinash Tiwari'
import random
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
import requests

discussion_url = settings.FEATURES['DISCUSSION_URL']
api_key = settings.FEATURES['discussion_api_key']


class Command(BaseCommand):
    """
    This command will send automatic emails based on various course events
    """
    args = ''
    help = 'Used to migrate user from edx to discourse'

    def handle(self, *args, **options):
        '''
          Operation: to send automatic emails based on various course events
          Input: None
          Output: None
          Developer : Avinash Tiwari
          Date: 13/February/2019
        '''
        print("===> Operation Start ===>")
        edx_user = User.objects.values('first_name', 'last_name', 'email',
                                       'username')
        index = 1
        discourse_users = []
        print("Getting Users from Discourse====>")
        while index != 0:
            try:
                url = discussion_url + "admin/users/list/active.json"
                querystring = {
                    "api_key": api_key,
                    "api_username": "staff",
                    "page": index
                }
                response = requests.request("GET", url, params=querystring)
                res = response.json()
                if len(res) > 0:
                    discourse_users += res
                    index += 1
                else:
                    index = 0
            except Exception as e:
                print("===> An Error Occurred '{}' at Page ({})===>".format(
                    e, index))
                index += 1
        print("Total users found===>", len(discourse_users))
        discourse_username = [user['email'] for user in discourse_users]
        user_not_in_edx = [
            user for user in edx_user
            if user['email'] not in discourse_username
        ]
        print("User to be created===>", len(user_not_in_edx))
        success_count = 0
        error_count = 0
        for user in user_not_in_edx:
            try:
                url = discussion_url + "users.json?api_key=" + api_key + "&api_username=staff"
                password = user['username'] + ''.join(
                    random.choice('0123456789ABCDEF') for i in range(3))
                data = {
                    "name": user['first_name'] + user['last_name'],
                    "email": user["email"],
                    "password": password,
                    "username": user["username"],
                    "active": True,
                    "trust_level": 1
                }
                response = requests.request("POST", url, data=data)
                if response.status_code == 200:
                    print("===> Created User '{}'===>".format(user))
                    success_count += 1
                else:
                    print("===> An Error Occurred '{}' for User ({})===>".format(
                        response.text, user))
                    error_count += 1
            except Exception as e:
                error_count += 1
                print("===> An Error Occurred '{}' for User ({})===>".format(
                    e, user))
                continue
        print("===> Operation Done ===>")
        print("* {} users migrated to discourse successfully !".format(
            success_count))
        print("* {} users are having trouble with the migrations".format(
            error_count))
