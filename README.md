# Firebase-Python-Write

Write data to firebase

Application dependencies in [requirements.txt](requirements.txt)

## App pre-requisites

1. Google account
2. Registration of project in firebase

## Rules of realtime firebase should be set to
```json
{
 "rules": {
   "emission_factor": {
     ".read": true,
     ".write": true
   },
  "resources" : {
       ".read": true,
     ".write": true
  }
 }
}
```

## Run application

1. Replace your value of option `database_url` under section `firebase` in [config/app.ini](config/app.ini) file  

2. Run `app.py` with [config/app.ini](config/app.ini) as parameter



## Helpful links
* [Save data to firebase via REST](https://firebase.google.com/docs/database/rest/save-data?authuser=1)

# ENTSOE-Client
