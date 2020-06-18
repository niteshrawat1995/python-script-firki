import csv
import os
import requests
from django.conf import settings


BASE_DIR = settings.BASE_DIR # /edx-platform/

# FILE_PATH = os.path.join(BASE_DIR, "docs", "class_6", "Class_6.csv")


CSV_PATH = os.path.join(BASE_DIR, "common/djangoapps/resources/management/commands/", "TickLinks_New Resources class_6c.csv")
PDF_PATH = os.path.join(BASE_DIR, "common/djangoapps/resources/management/commands/class_6")

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


def get_resource_data_from_csv(csv_path, pdf_path):
    if csv_path == "" and pdf_path == "":
        raise ValueError("SET THEM FIRST")

    with open(csv_path) as csv_file:
        csv_reader = list(csv.DictReader(csv_file))

    extension = ".pdf"

    objs_list = []

    for row in csv_reader:
        file_name = row.get("File_Name") + extension
        row["File_Name"] = file_name
        name = row.get("Name")
        subject = row.get("Subject")
        grade = row.get("Grade")
        desc_1 = row.get("Desc 1")
        desc_2 = row.get("Desc 2")
        desc_3 = row.get("Desc 3")
        
        desc_4 = desc_3.split("https")[0]
        row["Source_url"] = "https"+desc_3.split("https")[1].replace(" ","") 
        
        row["Full_Desc"] = ""
        if desc_1 and len(desc_1) > 0:
            row["Full_Desc"] += "<p> {} </p>".format(desc_1)
            del row['Desc 1']

        if desc_2 and len(desc_2) > 0:
            row["Full_Desc"] += "<p> {} </p>".format(desc_2)
            del row['Desc 2']

        if desc_4 and len(desc_4) > 0:
            row["Full_Desc"] += "<p> {} </p>".format(desc_4)
            del row['Desc 3']

        row["File_Path"] = get_media_file_path(row["File_Name"], pdf_path)
        objs_list.append(row)

    return objs_list


def get_media_file_path(filename, pdf_path):
    try:
        dirs = os.listdir(pdf_path)
    except:
        return ""
    if filename in dirs:
        return os.path.join(pdf_path, filename)
    else:
        return ""


def save_to_resource_model(obj_list):
    from django.core.files import File  # you need this somewhere
    from resources.models import *
    from django.contrib.auth.models import User

    user = User.objects.filter(is_staff=True).first()

    success_count, fail_count = 0, 0
    for obj in obj_list:
        subject, _ = Subject.objects.get_or_create(name__iexact=obj["Subject"])
        content_partner, _ = ContentPartner.objects.get_or_create(name__iexact="tickLinks")
        try:
            resource_obj = Resource.objects.get(name__iexact=obj["Name"])
        except:

            resource_obj = Resource(
                name=obj["Name"],
                description=obj["Full_Desc"],
                file_type=FileTypes.objects.get(name__iexact="Lesson Plans"),
                subject=subject,
                source_url=obj["Source_url"],
                content_partner=content_partner,
                file=File(open(obj["File_Path"], "rb")),
                created_by=user
            )            
        resource_obj.save()
        grades = Grade.objects.filter(name__iexact=ROMAN_MAP.get(str(obj["Grade"])))
        resource_obj.grade.add(*grades)
        resource_obj.save()


def main():
    obj_list = get_resource_data_from_csv(CSV_PATH, PDF_PATH)
    save_to_resource_model(obj_list)
    # print(obj_list[23])


from django.core.management.base import BaseCommand
class Command(BaseCommand):
    def handle(self, *args, **options):
        main()


