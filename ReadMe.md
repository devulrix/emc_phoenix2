# Conference App for the EMC Phoenix2 Event 2016 in Berlin 

Leveraging:
* Django 1.9
* Python 3
* Bootstrap
* Asynchronous tasks with celery and RabbitMQ
* S3 compatible (EMC ECS) storage backend
* Social Authentication
* REST Framework
* Cloud Foundry
* Twitter Streams
* New Relic

## Installation

Simplest way to test this app is to use ``Vagrant`` with ``vagrant up``. This will create a Fedora Virtualbox with all required packages and a python virtual environment.

## Configuration

### modify environments file for development
copy "environments.sh.example" environments.sh
modify environments.sh

### ECS

#### create ecs access keys
https://portal.ecstestdrive.com/

#### create buckets and corresponding CORS configuration (example below)
```
<CORSConfiguration>
 <CORSRule>
   <AllowedOrigin>http://www.example.com</AllowedOrigin>
   <AllowedMethod>PUT</AllowedMethod>
   <AllowedMethod>POST</AllowedMethod>
   <AllowedMethod>DELETE</AllowedMethod>
   <AllowedHeader>*</AllowedHeader>
 </CORSRule>
 <CORSRule>
   <AllowedOrigin>*</AllowedOrigin>
   <AllowedMethod>GET</AllowedMethod>
 </CORSRule>
</CORSConfiguration>
```
#### collectstatic at client
python manage.py collectstatic

### create social authentication

#### Google:
https://console.developers.google.com/

##### Create application
Create OAuth 2 Credentials -> Web application -> Authorized redirect URIs: http://app.domain.com/accounts/github/login/callback/

##### Enable API
Overview -> Google+ API -> Enable API

#### Twitter:
https://apps.twitter.com/

##### Create application
Create New App -> Callback URL: http://app.domain.com/accounts/twitter/login/callback/

#### Github:
https://github.com/settings/applications/new

##### Create application
Create New App -> Authorization callback URL: http://app.domain.com/accounts/github/login/callback/

#### Facebook:
https://developers.facebook.com/apps
Settings -> Advanced -> Valid OAuth redirect URIs: http://app.domain.com/accounts/facebook/login/callback/

#### cloud foundry

##### login to Cloud Foundry
```cf login -a https://api.run.pivotal.io```

##### create services
Example for Pivotal Web Service (run.pivotal.io)
```
cf create-service elephantsql turtle phoenix_db
cf create-service cloudamqp lemur phoenix_rabbitmq
cf create-service newrelic standard phoenix_newrelic

cf cups phoenix_ecs -p '{"HOST":"object.ecstestdrive.com","ACCESS_KEY_ID":"123456789@ecstestdrive.emc.com","SECRET_ACCESS_KEY":"ABCDEFGHIJKLMNOPQRSTUVWXYZ","PUBLIC_URL":"123456789.public.ecstestdrive.com","STATIC_BUCKET":"static","MEDIA_BUCKET":"public","SECURE_BUCKET":"secure"}'
cf cups phoenix_mail -p '{"HOST":"smtp.domain.local","USER":"django@domain.local","PASSWORD":"123456789","PORT":"25","TLS":"True", "DEFAULT_FROM":"noreply@domain.local"}'
cf cups phoenix_twitter -p '{"CONSUMER_KEY":"ABCDEFGHIJKLMNOPQRSTUVWXYZ","CONSUMER_SECRET":"ABCDEFGHIJKLMNOPQRSTUVWXYZ","ACCESS_TOKEN":"ABCDEFGHIJKLMNOPQRSTUVWXYZ","ACCESS_TOKEN_SECRET":"ABCDEFGHIJKLMNOPQRSTUVWXYZ"}'
cf cups phoenix_config -p '{"SECRET_KEY":"ABCDEFGHIJKLMNOPQRSTUVWXYZ","DEBUG":"False"}'
```
##### initial push for database creation
Script will create a superuser ``admin`` with password ``admin``
```cf push --no-route -c "bash ./init_db.sh" -i 1```

##### migrate database
```cf push phoenix-migrate --no-route -c "bash ./migrate.sh" -i 1  
cf delete phoenix-migrate```

##### push app
```cf push```

##### push celery
```cf push -f manifest-celery.yml```

##### push twitter-watcher
```cf push -f manifest-twitter-watcher.yml```