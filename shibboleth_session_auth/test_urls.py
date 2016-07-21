from django.conf.urls import patterns, include, url

urlpatterns = patterns('shibboleth_session_auth.views',
    url('^$', 'shibboleth_session_auth', name='shibboleth_session_auth')
)
