from aiohttp_security.abc import AbstractAuthorizationPolicy


class DictionaryAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, users):
        super().__init__()
        self.users = users

    async def authorized_userid(self, identity):
        """Retrieve authorized user id.
        Return the user_id of the user identified by the identity
        or 'None' if no user exists related to the identity.
        """
        if identity in self.users:
            return identity

    async def permits(self, identity, permission, context=None):
        """Check user permissions.
        Return True if the identity is allowed the permission in the
        current context, else return False.
        """
        # pylint: disable=unused-argument
        user = self.users.get(identity)
        if not user:
            return False
        return True


async def check_credentials(users, username, password):
    if username in users:
        return users.get(username) == password
    return False
