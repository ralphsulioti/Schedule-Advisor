from django.test import TestCase
from schedule_advisor.models import User, Class, Schedule
import requests

from schedule_advisor.settings import SIS_API_URL
from schedule_advisor.test_data import DANCE_EXAMPLE


def add_to_database(page_results):
    for result in page_results:
        db_equivalent = Class.objects.get_or_create(
            semester=result["strm"], class_number=result["class_nbr"]
        )[0]
        db_equivalent.subject = result["subject"]
        db_equivalent.catalog_number = result["catalog_nbr"]
        db_equivalent.class_section = result["class_section"]
        db_equivalent.component = result["component"]
        db_equivalent.units = result["units"]
        db_equivalent.source_data = result
        db_equivalent.name = result["descr"]
        db_equivalent.save()


class ScheduleAdvisorTestCase(TestCase):
    def test_not_admin_by_default(self):
        user = User.objects.get_or_create(username="testuser")[0]
        self.assertFalse(user.is_advisor)

    def test_data_loaded_correctly(self):
        json = requests.get(f"{SIS_API_URL}&term=1228&subject=DANC").json()
        add_to_database(json)
        qs = Class.objects.filter(semester="1228", subject="DANC")
        results = sorted([r.source_data for r in qs], key=lambda s: s["index"])
        self.assertEqual(DANCE_EXAMPLE, results)

    # Adds to schedule properly

    def test_adds_to_schedule_properly(self):
        user = User.objects.get_or_create(username="testuser")[0]
        add_to_database(DANCE_EXAMPLE)
        schedule = Schedule.objects.get_or_create(connected_user_id=user.id)[0]
        cl = Class.objects.get(semester="1228", subject="DANC", catalog_number="1400")
        cl.source_data["enrl_stat"] = "O"
        cl.save()
        schedule.add_class(cl)
        self.assertEqual(1, schedule.classes.count())

    # Removes from schedule properly
    def test_removes_from_schedule_properly(self):
        user = User.objects.get_or_create(username="testuser")[0]
        add_to_database(DANCE_EXAMPLE)
        schedule = Schedule.objects.get_or_create(connected_user_id=user.id)[0]
        cl = Class.objects.get(semester="1228", subject="DANC", catalog_number="1400")
        schedule.classes.add(cl)
        schedule.remove_class(cl)
        self.assertEqual(0, schedule.classes.count())

    # Time conflicts verified
    def test_time_conflict_fails(self):
        user = User.objects.get_or_create(username="testuser")[0]
        add_to_database(DANCE_EXAMPLE)
        schedule = Schedule.objects.get_or_create(connected_user_id=user.id)[0]
        cl = Class.objects.get(semester="1228", subject="DANC", catalog_number="1400")
        schedule.classes.add(cl)
        cl2 = Class.objects.get(semester="1228", subject="DANC", catalog_number="3640")
        self.assertFalse(schedule.class_can_be_added(cl2))

    def test_time_conflict_passes(self):
        user = User.objects.get_or_create(username="testuser")[0]
        add_to_database(DANCE_EXAMPLE)
        schedule = Schedule.objects.get_or_create(connected_user_id=user.id)[0]
        cl = Class.objects.get(semester="1228", subject="DANC", catalog_number="1400")
        schedule.classes.add(cl)
        cl2 = Class.objects.get(semester="1228", subject="DANC", catalog_number="2220")
        self.assertTrue(schedule.class_can_be_added(cl2))
