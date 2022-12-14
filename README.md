# outreach-opsbot
A Discord bot for managing server operations in a k8s environment.  

The goal is to execute simple tasks such as backup restoration by launching kubernetes jobs via this service.


## Install
This bot listens on port `8080` as a Discord webhook.

1. Update `admins.txt` with the Discord users you'd like to have access
1. Build and run the container, and point the Discord app at it
3. Place the app in your admin channel

Required ENV:
```
DISCORD_TOKEN
NAMESPACE
GCP_GS_BUCKET
```

Required mounts:
```
A k8s ServiceAccount
/etc/gcp-sa/service-account.json
```

Required k8s permissions:
| Resource | Verbs |
|:--|:--|
| jobs | get, list, create |
