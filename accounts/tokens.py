from datetime import timedelta
from django.conf import settings
from django.core import signing

ACTIVATION_SALT = 'accounts.activation'


def make_activation_token(user):
    """بيعمل توكن (كود) مشفر فيه رقم المستخدم بس"""
    return signing.dumps({'uid': user.pk}, salt=ACTIVATION_SALT)


def check_activation_token(token):
    """بيرجع رقم المستخدم لو التوكن صحيح ومش منتهي، وإلا بيرجع None"""
    max_age = timedelta(hours=settings.ACTIVATION_LINK_EXPIRY_HOURS).total_seconds()
    try:
        data = signing.loads(token, salt=ACTIVATION_SALT, max_age=max_age)
    except signing.BadSignature:
        return None
    return data.get('uid')