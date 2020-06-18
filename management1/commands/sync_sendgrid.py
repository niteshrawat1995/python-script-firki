import os
import json
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
        Sync user data with sendgrid
    """

    help = "Sync user data with sendgrid"

    def handle(self, *args, **options):

        users = User.objects.all()
        url = "https://api.sendgrid.com/v3/contactdb/recipients"
        user_data = []
        count = 0

        for user in users:
            if count<1000:
                user_data.append(
                    {
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    }
                )
                count += 1
            else:
                try:
                    payload = json.dumps(user_data)
                    headers = {
                        'authorization': "Bearer {}".format(settings.EMAIL_HOST_PASSWORD),
                        'content-type': "application/json"
                        }
                    response = requests.request("POST", url, data=payload, headers=headers)
                    user_data = []
                    count = 0

                except Exception as ex:
                    print(ex)

        payload = json.dumps(user_data)
        headers = {
                    'authorization': "Bearer {}".format(settings.EMAIL_HOST_PASSWORD),
                    'content-type': "application/json"
                    }
        response = requests.request("POST", url, data=payload, headers=headers)
