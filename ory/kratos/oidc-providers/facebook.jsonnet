local claims = std.extVar('claims');
{
  identity: {
    traits: {
      // The email might be empty if the user hasn't granted permissions for the email scope.
      [if 'email' in claims then 'email' else null]: claims.email,
    },
  },
}
