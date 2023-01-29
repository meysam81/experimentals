# Session Store

## Create PEM keypair

```bash
step crypto keypair server.pub server.key --kty RSA --size 4096
```

Optionally:

```bash
--insecure --no-password
```

## Create JWK from PEM keypair

```bash
step crypto jwk create jwk.pub.json jwk.json --from-pem server.key --alg RS384
```
