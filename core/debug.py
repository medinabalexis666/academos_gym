from django.conf import settings

def trampa():
    if settings.DEBUG:
        import ipdb; ipdb.set_trace()