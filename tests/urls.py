from django.conf.urls import url

from shibboleth_session_auth.views import shibboleth_session_auth

urlpatterns = [
    url('^$', shibboleth_session_auth, name='shibboleth_session_auth'),
]
