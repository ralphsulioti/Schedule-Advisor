from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from schedule_advisor.forms import ClassSearchForm, AdviseeChoiceForm
from schedule_advisor.models import Schedule, Class, User
from django.contrib import messages


def search_view(request):
    results = None
    if request.method == "POST":
        form = ClassSearchForm(request.POST)
        if form.is_valid():
            # results = ClassSearchForm.get_results(form.cleaned_data)
            results = ClassSearchForm.get_results_from_database(form.cleaned_data)
    else:
        form = ClassSearchForm()
    return render(
        request, "schedule_advisor/index.html", {"form": form, "results": results}
    )
def home_view(request):
    return render(
        request, "schedule_advisor/home.html"
    )


def schedule_view(request):
    days_of_week = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]
    days_from_abbrev = {day[:2]: day for day in days_of_week}
    if not request.user.is_authenticated:
        messages.add_message(request, messages.ERROR, "You are not logged in!")
        return HttpResponseRedirect("/")
    u = User.objects.get_or_create(username=request.user.username)[0]
    if u.is_advisor:
        messages.add_message(request, messages.ERROR, "You are not a student!")
        return HttpResponseRedirect("/")
    schedule = Schedule.objects.get_or_create(connected_user_id=u.id)[0]
    schedule_by_day = {day: list() for day in days_of_week}
    for cl in schedule.classes.all():
        for day in cl.meeting_days():
            if day not in days_from_abbrev:
                schedule_by_day[day] = [cl]
            else:
                schedule_by_day[days_from_abbrev[day]].append(cl)
    for day, classes in schedule_by_day.items():
        if day not in days_of_week:
            classes.sort(key=lambda c: c.name)
            continue
        abbrev = day[:2]
        classes.sort(
            key=lambda c: tuple(
                int(i) for i in c.meeting_days()[abbrev][0].split(".")[:3]
            )
        )
    return render(
        request,
        "schedule_advisor/schedule.html",
        {
            "schedule_by_day": schedule_by_day,
            "days_of_week": days_of_week,
            "schedule": schedule,
        },
    )


def class_schedule_change_view(request):
    u = User.objects.get_or_create(username=request.user.username)[0]
    if u.is_advisor:
        messages.add_message(request, messages.ERROR, "You are not a student!")
        return HttpResponseRedirect("/")
    if request.method == "POST":
        action = request.POST["action"]
        try:
            if action == "Add to Schedule":
                schedule = Schedule.objects.get_or_create(
                    connected_user_id=request.user.id
                )[0]
                new_class = Class.objects.get_or_create(
                    semester=request.POST["semester"],
                    class_number=int(request.POST["class_number"]),
                )[0]
                schedule.add_class(new_class)
                schedule.reset_advisor()
                messages.add_message(
                    request, messages.SUCCESS, "Course successfully added to schedule!"
                )
            elif action == "Remove from Schedule":
                schedule = Schedule.objects.get_or_create(
                    connected_user_id=request.user.id
                )[0]
                old_class = Class.objects.get_or_create(
                    semester=request.POST["semester"],
                    class_number=int(request.POST["class_number"]),
                )[0]
                schedule.remove_class(old_class)
                schedule.reset_advisor()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    "Course successfully removed from schedule!",
                )
            else:
                messages.add_message(
                    request, messages.ERROR, "Unable to update schedule!"
                )
        except:
            messages.add_message(request, messages.ERROR, "Unable to update schedule!")
        # https://stackoverflow.com/questions/35796195/how-to-redirect-to-previous-page-in-django-after-post-request
        return HttpResponseRedirect(request.headers.get("referer", "/"))


def advisor_view(request):
    u = User.objects.get_or_create(username=request.user.username)[0]
    if not u.is_advisor:
        messages.add_message(request, messages.ERROR, "You are not an advisor!")
        return HttpResponseRedirect("/")
    else:
        schedules = None
        days_of_week = None
        schedule_by_day = None
        query = None
        advisees = User.objects.filter(advisor=request.user)
        if request.method == "GET":
            query = request.GET.get("q", None)
            if query:
                query = User.objects.filter(
                    Q(is_advisor=False)
                    & (
                        Q(first_name__icontains=query)
                        | Q(last_name__icontains=query)
                        | Q(username__icontains=query)
                    )
                )
        elif request.method == "POST":
            advisee_id = request.POST.get("advisee_id")
            schedules = Schedule.objects.filter(connected_user_id=advisee_id)
            days_of_week = [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
            ]
            days_from_abbrev = {day[:2]: day for day in days_of_week}
            u = User.objects.get_or_create(id=advisee_id)[0]
            schedule = Schedule.objects.get_or_create(connected_user_id=u.id)[0]
            schedule_by_day = {day: list() for day in days_of_week}
            for cl in schedule.classes.all():
                for day in cl.meeting_days():
                    if day not in days_from_abbrev:
                        schedule_by_day[day] = [cl]
                    else:
                        schedule_by_day[days_from_abbrev[day]].append(cl)
            for day, classes in schedule_by_day.items():
                if day not in days_of_week:
                    classes.sort(key=lambda c: c.name)
                    continue
                abbrev = day[:2]
                classes.sort(
                    key=lambda c: tuple(
                        int(i) for i in c.meeting_days()[abbrev][0].split(".")[:3]
                    )
                )
        return render(
            request,
            "schedule_advisor/advisor_schedules.html",
            {
                "advisees": advisees,
                "schedules": schedules,
                "days_of_week": days_of_week,
                "schedule_by_day": schedule_by_day,
                "query": query,
            },
        )


def advisee_change_view(request):
    u = User.objects.get_or_create(username=request.user.username)[0]
    if not u.is_advisor:
        messages.add_message(request, messages.ERROR, "You are not an advisor!")
        return HttpResponseRedirect("/")
    else:
        action = request.POST["action"]
        try:
            if action == "Add":
                advisee = User.objects.get_or_create(username=request.POST["advisee"])[
                    0
                ]
                advisor = User.objects.get_or_create(username=request.POST["advisor"])[
                    0
                ]
                advisee.advisor = advisor
                advisee.save()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f"You are now the advisor for {advisee.get_full_name()}!",
                )
            elif action == "Remove":
                advisee = User.objects.get_or_create(username=request.POST["advisee"])[
                    0
                ]
                advisee.advisor = None
                advisee.save()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f"You are no longer the advisor for {advisee.get_full_name()}!",
                )
            else:
                messages.add_message(
                    request, messages.ERROR, "Unable to update schedule!"
                )
        except:
            messages.add_message(
                request,
                messages.ERROR,
                "Unable to edit advisor information for student!",
            )
        # https://stackoverflow.com/questions/35796195/how-to-redirect-to-previous-page-in-django-after-post-request
        return HttpResponseRedirect(request.headers.get("referer", "/"))


def class_schedule_visible_view(request):
    if request.method == "POST":
        try:
            u = User.objects.get_or_create(username=request.user.username)[0]
            if u.is_advisor:
                messages.add_message(request, messages.ERROR, "You are not a student!")
                return HttpResponseRedirect("/")
            if not u.advisor:
                messages.add_message(request, messages.ERROR, "You do not have an advisor!")
                return HttpResponseRedirect("/")
            s = Schedule.objects.get_or_create(connected_user=u)[0]
            visibility = request.POST.get("visible", False)
            s.visible = visibility == "on"
            s.reset_advisor()
            messages.add_message(
                request,
                messages.SUCCESS,
                f"Your schedule is{'' if visibility else ' no longer'} visible to {u.advisor.get_full_name()}!",
            )
        except:
            messages.add_message(
                request,
                messages.ERROR,
                "Unable to edit schedule visibility!",
            )
        return HttpResponseRedirect(request.headers.get("referer", "/"))


def schedule_approval_view(request):
    u = User.objects.get_or_create(username=request.user.username)[0]
    if not u.is_advisor:
        messages.add_message(request, messages.ERROR, "You are not an advisor!")
        return HttpResponseRedirect("/")
    if request.method == "POST":
        try:
            schedule = Schedule.objects.get_or_create(id=int(request.POST["schedule"]))[0]
            schedule_user: User = schedule.connected_user
            if schedule_user.advisor != u:
                messages.add_message(request, messages.ERROR, "You are not this student's advisor!")
                return HttpResponseRedirect("/schedules")
            decision = request.POST["decision"]
            if decision == "true":
                decision = True
                messages.add_message(
                    request, messages.SUCCESS, "You have approved this schedule!"
                )
            elif decision == "false":
                decision = False
                messages.add_message(
                    request, messages.SUCCESS, "You have rejected this schedule!"
                )
            else:
                decision = None
            schedule.approved = decision
            schedule.save()
        except:
            messages.add_message(
                request,
                messages.ERROR,
                "Unable to update schedule approval status!",
            )
    return HttpResponseRedirect(request.headers.get("referer", "/"))
