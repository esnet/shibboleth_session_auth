import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, \
                        HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import get_script_prefix

logger = logging.getLogger(__name__)

def shibboleth_session_auth(request):
    """Authenticate a session using Shibboleth.

    This allows Shibboleth to be one of many options for authenticating to
    the site. Instead of protecting the whole site via Shibboleth, we protect
    a single view (this view).  The view will authenticate the user using
    the attributes passed in via request.META to authenticate the user.

    """

    idp_attr = settings.SHIBBOLETH_SESSION_AUTH['IDP_ATTRIBUTE']
    idp = request.META.get(idp_attr)
    if not idp:
        logger.error("IdP header missing (%s)", idp_attr)
        return HttpResponseBadRequest("Invalid response from IdP")

    if idp not in settings.SHIBBOLETH_SESSION_AUTH['AUTHORIZED_IDPS']:
        logger.info("Unauthorized IdP: %s", idp)
        return HttpResponseForbidden("unauthorized IdP: {}".format(idp))

    user_attrs = {}

    for http_attr, user_attr, required in settings.SHIBBOLETH_SESSION_AUTH['USER_ATTRIBUTES']:
        user_attrs[user_attr] = request.META.get(http_attr, None)
        if required and user_attrs[user_attr] is None:
            logger.error("SSO missing attribute: %s", user_attr)
            return HttpResponseBadRequest("Invalid response from IdP")

    try:
        user = User.objects.get(username=user_attrs['username'])
    except User.DoesNotExist:
        user = User(**user_attrs)
        user.set_unusable_password()
        user.save()

    if idp in settings.SHIBBOLETH_SESSION_AUTH['GROUPS_BY_IDP']:
        for group_name in settings.SHIBBOLETH_SESSION_AUTH['GROUPS_BY_IDP'][idp]:
            try:
                group = Group.objects.get(name=group_name)
            except Group.DoesNotExist:
                logger.info("creating group %s (locally configured for IdP %s)", group_name, idp)
                continue

            if group not in user.groups.all():
                user.groups.add(group)
                logger.info("adding user %s to group %s", user.username, group.name)

    group_attr = settings.SHIBBOLETH_SESSION_AUTH['GROUP_ATTRIBUTE']
    if group_attr in request.META:
        for group_name in request.META[group_attr].split(";"):
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                logging.info("creating group %s (remotely provided by IdP %s)", group_name, idp)

            if group not in user.groups.all():
                group.user_set.add(user)
                logger.info("adding user %s to group %s", user.username, group.name)

    user = authenticate(remote_user=user.username)
    login(request, user)

    if "next" in request.GET:
        redirect_target = request.GET['next']
    else:
        redirect_target = get_script_prefix()

    return HttpResponseRedirect(redirect_target)
