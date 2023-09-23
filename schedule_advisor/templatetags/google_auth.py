from schedule_advisor.settings import google_client_id
from django import template

register = template.Library()


@register.simple_tag
def client_id():
    return google_client_id


@register.simple_tag
def get_current_host(request) -> str:
    scheme = request.is_secure() and "https" or "http"
    return f"{scheme}://{request.get_host()}"
