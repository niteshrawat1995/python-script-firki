from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from xmodule.modulestore.django import modulestore
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


from mx_webinars.models import Webinar
from resources.models import Resource
from mx_discourse.models import Content



class Command(BaseCommand):
    """
    Command to migrate/create Course, MX_Webinar and Resources instances into Content instances
    """

    def handle(self, *args, **options):
        print("===> Operation Start ===>")
        
        user = User.objects.filter(is_staff=True).first()
        mx_webinars = Webinar.objects.all()
        resources = Resource.objects.all()
        courses = CourseOverview.objects.all()

        mx_webinar_count = 0
        resources_count = 0
        courses_count = 0

        print("===> Migrating MX_Webinar instances Start ===>")
        for mx_webinar in mx_webinars:
            obj, created = Content.objects.update_or_create(
                source_id = mx_webinar.id,
                rs_type = "W",
                defaults = {
                    "title":mx_webinar.title,
                    "created_by": user
                }
            )
            if created:
                mx_webinar_count += 1

        print("===> Migrating MX_Webinar instances Ends , Total new content created: {}===>".format(mx_webinar_count))


        print("===> Migrating Resources instances Start ===>")

        for resource in resources:
            obj, created = Content.objects.update_or_create(
                source_id=resource.id,
                rs_type = "R",
                defaults = {
                    "title": resource.name,
                    "created_by":user
                }
            )
            if created:
                resources_count += 1
        print("===> Migrating Resources instances Ends, Total new content created: {}===>".format(resources_count))

        print("===> Migrating CourseOverview instances Start ===>")

        for course in courses:
            obj, created = Content.objects.get_or_create(
                source_id=course.id,
                rs_type = "C",
                defaults = {
                    "title": course.display_name,
                    "created_by":user
                }
            )
            if created:
                courses_count += 1
        print("===> Migrating CourseOverview instances Ends, Total new content created: {}===>".format(courses_count))


        print("===> Operation Start ===>")
        







        





        
             



