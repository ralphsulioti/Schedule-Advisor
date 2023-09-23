from datetime import datetime
from django import template

from schedule_advisor.models import User, Schedule
from schedule_advisor.forms import ClassSearchForm

register = template.Library()


@register.simple_tag
def meeting_string(meeting) -> str:
    try:
        formatted_start_time = convert_date(meeting["start_time"])
        formatted_end_time = convert_date(meeting["end_time"])
        return f"{meeting['days']} {formatted_start_time} - {formatted_end_time} from {meeting['start_dt']} to {meeting['end_dt']} in {meeting['facility_descr']}"
    except ValueError:
        return "To Be Announced"


@register.simple_tag
def current_semester() -> str:
    if not ClassSearchForm.SEMESTER_CHOICES:
        return "N/A"
    return ClassSearchForm.SEMESTER_CHOICES[0][1]


def convert_date(input_string: str) -> str:
    time_input_format = "%H.%M.%S.%f"
    time_output_format = "%-I:%M:%S %p"
    return datetime.strptime(input_string.split("-")[0], time_input_format).strftime(
        time_output_format
    )


@register.inclusion_tag("schedule_advisor/class_action.html")
def class_can_be_added(schedule, new_class) -> dict:
    return {
        "add": schedule.class_can_be_added(new_class),
        "delete": new_class in schedule.classes.all(),
        "closed": new_class.source_data["enrl_stat"] == "C",
        "waitlist": new_class.source_data["enrl_stat"] == "W",
        "open": new_class.source_data["enrl_stat"] == "O",
        "semester": new_class.semester,
        "class_number": new_class.class_number,
    }


@register.inclusion_tag("schedule_advisor/advisee_action.html")
def advisee_can_be_added(advisor, advisee) -> dict:
    advisor = User.objects.get_or_create(username=advisor.username)[0]
    advisee = User.objects.get_or_create(username=advisee.username)[0]
    approved = Schedule.objects.get_or_create(connected_user=advisee)[0].approved
    return {
        "is_advisor_advisee": advisee.advisor == advisor,
        "has_other_advisor": advisee.advisor is not None and advisee.advisor != advisor,
        "advisor": advisor.username,
        "advisee": advisee.username,
        "approved": approved,
    }
