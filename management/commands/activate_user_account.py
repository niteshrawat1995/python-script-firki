__author__ = 'Kritika Arora'
from django.db import connections
from django.conf import settings
from django.core.management.base import BaseCommand


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def execute_edx_query(query):
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            data = dictfetchall(cursor)
            print("Connected to Edx Database")
            return (data)
    except Exception as e :
        print("Unable to connect to Edx Database:{}".format(e))
        raise NotImplementedError(
            "Please add DB connection string in the settings.py file!")
        return None

def execute_postgres_update_query(query):
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            print("Connected to Edx Database for updation")
            return True
    except Exception as e :
        print("Unable to connect to edx Database:{}".format(e))
        raise NotImplementedError(
            "Please add default DB connection string in the settings.py file!")
        return None




    
class Command(BaseCommand):
    """
    This command will add users(from csv) to discourse (that are not in discourse earlier)
    """
    args = ''
    help = 'Used to migrate user from edx to discourse'

    # def add_arguments(self, parser):
    #     parser.add_argument('csv_path')

    def handle(self, *args, **options):
        '''
          Operation: to activate user account
          Output: None
          Developer : 'Kritika Arora'
          Date: 7/September/2019
        '''
        print("===> Operation Start ===>")
        import pudb;pudb.set_trace()
        select_query="select id from auth_user where is_active=0;"
        data=execute_edx_query(select_query)

        print('upadating start')
        for rec in data:
            print("updating id==>",rec['id'])
            update_query="UPDATE auth_user SET is_active = 1 WHERE id ={};".format(rec['id'])
            is_updated=execute_postgres_update_query(update_query)
            if is_updated:
                print('updated')
            else:
                print(' NOt updated')

        print("===> Operation End ===>")
