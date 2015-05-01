# Openstack Integration Pack

StackStorm pack for OpenStack integration.

## Configuration

Pack configuration requires to URLs and of the openstack APIs and an authetication mechanism. There are two way to supply this information :

### Token based

Supply an already acquired token and a URL pointing to the service API. Both of these would have to be acquired from the service catalog.

To acquire a token -

```
curl -s -X POST $OS_AUTH_URL/tokens -H "Content-Type: application/json" -d '{"auth": {"tenantName": "'"$OS_TENANT_NAME"'", "passwordCredentials": {"username": "'"$OS_USERNAME"'", "password": "'"$OS_PASSWORD"'"}}}' | python -m json.tool
```
See the [OpenStack manual](http://docs.openstack.org/api/quick-start/content/index.html#authenticate) for more information on above command.

```yaml
---
token:
    OS_TOKEN: "xxxxxxxxxxxxxxxxxxxx"
    OS_URL: "http://{API_IP}:{API_PORT}/v2/{TENANT_ID}"
```

### Password based

Tokens are ephemeral and typical expiry is short; in those cases it might be preferred to use the password based approach.

```yaml
---
password:
    OS_AUTH_URL: # authentication url
    OS_TENANT_ID: # id of the tenant
    OS_TENANT_NAME: # name of the tenant
    OS_USERNAME: # username
    OS_PASSWORD: # password
```

## Actions

[Description of all the available actions]

## Sensors

No sensors in this pack.
