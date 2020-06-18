import os
import json
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from django.conf import settings
from resources.models import Resource,FileTypes
import csv

# file="common/djangoapps/resources/management/resource_mapping.csv"
file = 'common/djangoapps/resources/management/commands/resource_mapping.csv'
print(file)

def upadtemapping(resourceobj):
    pass
    


def getResource(title,contentpartner):
    try:
        obj=Resource.objects.get(name=title,content_partner__name=contentpartner)
        return obj
    except Exception as e:
        print (e)
    return None

def get_contenttype_obj(typename):
    try:
        id=FileTypes.objects.get(name=typename)
        return id
    except  Exception as e:
        print(e)
    return None

def exceute_script():
    with open(file)as f:
        reader = csv.DictReader(f)
        for row in reader:
            print("---------------------------------------------------------------------------------")
            print(row)
            resourceobj=getResource(row['Name'],row['Content_Patner'])
            if resourceobj:
                obj=get_contenttype_obj(row['Content_type'])
                if obj:
                    resourceobj.file_type=obj
                    resourceobj.save()
                else:
                    print('No filetype for:',row['Content_type'])            
            else:
                print("No resources mapping",row['Name'])
            



class Command(BaseCommand):
    """
        Sync user data with sendgrid
    """

    help = "Sync user data with sendgrid"

    def handle(self, *args, **options):
        # pass
        exceute_script()
        # resourceobj=qetResource(title,contentpartner)
        # upadtemapping(resourceobj)

       