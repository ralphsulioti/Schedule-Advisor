from django.core.management.base import BaseCommand
from schedule_advisor.settings import SIS_API_URL
from schedule_advisor.forms import ClassSearchForm
from schedule_advisor.models import Class

import requests


class Command(BaseCommand):
    help = "Gets data from SIS and saves it to the database."

    def handle(self, *args, **kwargs):
        current_semester = ClassSearchForm.SEMESTER_CHOICES[0][0]
        url = SIS_API_URL + f"&term={current_semester}"
        current_page = 0
        results = []
        all_classes_for_term = Class.objects.filter(semester=current_semester)
        class_numbers_db = {db_class.class_number for db_class in all_classes_for_term}
        while True:
            current_page += 1
            page_results = requests.get(f"{url}&page={str(current_page)}").json()
            if not page_results:
                break
            results += page_results
            for result in page_results:
                db_equivalent = Class.objects.get_or_create(
                    semester=result["strm"], class_number=result["class_nbr"]
                )[0]
                # if result == db_equivalent.source_data:
                #     continue
                db_equivalent.subject = result["subject"]
                db_equivalent.catalog_number = result["catalog_nbr"]
                db_equivalent.class_section = result["class_section"]
                db_equivalent.component = result["component"]
                db_equivalent.units = result["units"]
                db_equivalent.source_data = result
                db_equivalent.name = result["descr"]
                db_equivalent.save()
        class_numbers_api = {api_class["class_nbr"] for api_class in results}
        classes_to_delete = class_numbers_db.difference(class_numbers_api)
        for class_to_delete in classes_to_delete:
            db_class = Class.objects.get(class_number=class_to_delete)
            db_class.delete()

