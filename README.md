[![Build Status](https://travis-ci.org/esnet/shibboleth_session_auth.svg?branch=master)](https://travis-ci.org/esnet/shibboleth_session_auth) [![Coverage Status](https://coveralls.io/repos/github/esnet/shibboleth_session_auth/badge.svg?branch=master)](https://coveralls.io/github/esnet/shibboleth_session_auth?branch=master)

# shibboleth_session_auth 
## Simplistic Shibboleth integration for Django sessions

### Apache config

This code has only been tested with `mod_shib` for Apache.

Here's the config we use:

```
<Location /shibboleth-sso/>
  AuthType shibboleth
  ShibCompatWith24 On
  ShibRequestSetting requireSession true
  Require shib-attr member staff
/Location>
```

You may want to tweak or remove the `Require` line depending on your needs.
As it is, it requires users to be a member of group `staff` in order to be
able to authenticate.

### Django configuration

You'll need to add an entry in your `urls.py`, similar to this:

```
from shibboleth_session_auth.views import shibboleth_session_auth

urlpatterns += [
    url(r'^shibboleth-sso/', shibboleth_session_auth, name="esnet-sso"),
]
```

Note that we use `shibboleth-sso` both here and in the Apache config.
