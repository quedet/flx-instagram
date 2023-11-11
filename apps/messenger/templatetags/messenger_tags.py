from django import template

register = template.Library()


@register.filter
def room_name(value, args):
    user = value.users_subscribed.exclude(username=args).first()
    return user
