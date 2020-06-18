import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

import csv
import os
import requests
import urlparse
from django.conf import settings

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

BASE_DIR = settings.BASE_DIR # /edx-platform/

# FILE_PATH = os.path.join(BASE_DIR, "docs", "class_6", "Class_6.csv")


CSV_PATH = os.path.join(BASE_DIR, "common/djangoapps/resources/management/commands", "wikiHow_resource_video.csv")
# PDF_PATH = os.path.join(BASE_DIR, "common/djangoapps/resources/management/commands/class_6")

# print(CSV_PATH)
# print(PDF_PATH)


ROMAN_MAP = {
    "1": "I",
    "2": "II",
    "3": "III",
    "4": "IV",
    "5": "V",
    "6": "VI",
    "7": "VII",
    "8": "VIII",
    "9": "IX",
    "10": "X",
    "11": "XI",
    "12": "XII"
}


def get_resource_data_from_csv(csv_path):
    if csv_path == "":
        raise ValueError("SET THEM FIRST")

    with open(csv_path) as csv_file:
        old_csv_reader = list(csv.DictReader(csv_file))
        csv_reader = []
        for row in old_csv_reader:
            encoded_row = {}
            for key, item in row.iteritems():
                try:
                    encoded_row[key] = item.decode("utf8")
                    # encoded_row[key] = item
                except:
                    import pdb; pdb.set_trace()

            csv_reader.append(encoded_row)
             

    # extension = ".pdf"

    objs_list = []

    for row in csv_reader:
        # file_name = row.get("File_Name") + extension
        # row["File_Name"] = file_name
        name = row.get("\xef\xbb\xbfName")
        subject = row.get("Subject")
        grade = row.get("Grade")
        desc_1 = row.get("Desc_1")
        desc_2 = row.get("Desc_2")
        link = row.get("Link")
        source_url = row.get("Source_url")
        
        if(link.find("v=") != -1):
            url_data = urlparse.urlparse(link)
            query = urlparse.parse_qs(url_data.query)
            video_id = query["v"][0]
        else:
            video_id = link.rsplit('/', 1)[1]


        row["Link"] = video_id
        
        row["Full_Desc"] = ""
        logging.info(desc_1)
        if desc_1 and len(desc_1) > 0:
            row["Full_Desc"] += "<p> {} </p>".format(desc_1)
            del row['Desc_1']

        if desc_2 and len(desc_2) > 0:
            row["Full_Desc"] += "<p> {} </p>".format(desc_2)
            del row['Desc_2']

        # if desc_3 and len(desc_3) > 0:
        #     row["Full_Desc"] += "<p> {} </p>".format(desc_3)
        #     del row['Desc_3']

        # row["File_Path"] = get_media_file_path(row["File_Name"], pdf_path)
        objs_list.append(row)

    return objs_list


# def get_media_file_path(filename, pdf_path):
#     try:
#         dirs = os.listdir(pdf_path)
#     except:
#         import pdb; pdb.set_trace()
#         return ""
#     if filename in dirs:
#         return os.path.join(pdf_path, filename)
#     else:
#         import pdb; pdb.set_trace()
#         log.error("Not able to find file : {}".format(filename))
#         return ""


def save_to_resource_model(obj_list):
    # from django.core.files import File  # you need this somewhere
    from resources.models import *
    from django.contrib.auth.models import User
    user = User.objects.filter(is_staff=True).first()
    success_count, fail_count = 0, 0
    for obj in obj_list:
        #subject, _ = Subject.objects.get_or_create(name__iexact=obj["Subject"])
        try:
            content_partner = ContentPartner.objects.get(name__iexact="wikiHow")
        except:
            content_partner = ContentPartner.objects.create(name="wikiHow")
	
	try:
            subject = Subject.objects.get(name__iexact=obj["Subject"])
        except:
            subject = Subject.objects.create(name=obj["Subject"])

        #content_partner, _ = ContentPartner.objects.get_or_create(name__iexact="Tickle Partner")
        try:
            resource_obj = Resource.objects.get(name__iexact=obj["\xef\xbb\xbfName"])
        except:
            logging.info(obj["\xef\xbb\xbfName"])
            resource_obj = Resource(
                name=obj["\xef\xbb\xbfName"],
                description= obj["Full_Desc"],
                file_type=FileTypes.objects.get(name__iexact="Content Videos"),
                subject=subject,
                source_url=obj["Source_url"],
                link="https://www.youtube.com/embed/"+obj["Link"],
                content_partner=content_partner,
                # file=File(open(obj["File_Path"], "rb")),
                created_by=user
            )

        try:
            resource_obj.save()
            # grades = Grade.objects.filter(name__iexact=ROMAN_MAP.get(str(obj["Grade"])))
            grades_list = list(map(lambda x:x.strip(), obj["Grade"].strip().split(",")))
            roman_grades = [ROMAN_MAP.get(grade) for grade in grades_list]
            grades = Grade.objects.filter(name__in=roman_grades)
            resource_obj.grade.add(*grades)
            resource_obj.save()
        except Exception as e:
            log.error("Unable to save : obj['name']={}".format(obj["\xef\xbb\xbfName"]))
            log.error(e)


def main():
    obj_list = get_resource_data_from_csv(CSV_PATH)
    save_to_resource_model(obj_list)
    # print(obj_list[23])


from django.core.management.base import BaseCommand
class Command(BaseCommand):
    def handle(self, *args, **options):
        main()


