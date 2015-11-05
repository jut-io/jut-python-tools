# jut-tools

[![Build Status](https://travis-ci.org/jut-io/jut-python-tools.svg)](https://travis-ci.org/jut-io/jut-python-tools)

Command line tools for interacting with your Jut instance.  

# Table of Contents

  * [Requirements](#requirements)
  * [Installation](#installation)
  * [Upgrading](#upgrading)
  * [Config Command](#config-command)
    * [First time configuration](#first-time-configuration)
    * [Using multiple configurations](#using-multiple-configurations)
    * [Removing configurations](#removing-configurations)
  * [Jobs Command](#jobs-command)
    * [Check which jobs are running](#check-which-jobs-are-running)
    * [Kill a running job](#kill-a-running-job)
    * [Connect to a persisten job](#connect-to-a-persistent-job) * [Run Command](#run-command)
    * [Getting JSON data out of Jut](#getting-json-data-out-of-jut)
    * [Getting a list of things out of Jut](#getting-a-list-of-things-out-of-jut)
    * [Reconstructing log lines from all your hosts with Jut](#reconstructing-log-lines-from-all-your-hosts-with-jut)
    * [Getting a desktop notification with Jut](#getting-a-desktop-notification-with-jut)
  * [Upload Command](#upload-command)
    * [Upload a JSON file](#upload-a-json-file)
    * [Uploading a directory of JSON files](#uploading-a-directory-of-json-files)
  * [Jut Python API](#jut-python-api)
    * [Auth API](#auth-api)
    * [Accounts API](#accounts-api)
    * [Deployments API](#deployments-api)
    * [Data Engine API](#data-engine-api)
  * [Development](#development)
    * [Running Tests](#running-tests)
    * [Running a specific test](#running-a-specific-test)

## Requirements

 * Python 2.7.9+

We ask for 2.7.9+ because otherwise you may run into the following 
security message:
```
InsecurePlatformWarning: A true SSLContext object is not available. 
This prevents urllib3 from configuring SSL appropriately and may cause certain SSL connections to fail. 
For more information, see https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning.
```

## Installation

Installation is as easy as**(*)**:

```
pip install jut-tools
```

or 

```
easy_install jut-tools
```


That will get you the latest official build from pypi but if you want to use
the bleeding master code you can also use:

**(*)** You may need to use `sudo` with the above commands if you are not using a
virtualenv or don't have a userspace python installation.

## Upgrading

If attempting to upgrade to the latest and greatest build just add the `-U`
option like so:

```
pip install -U jut-tools
```

or 

```
easy_install -U jut-tools
```

## Config Command

### First time configuration

Once you've installed the jut python tools you should immediately run:

```
jut config add
```

in order to add your first configuration. We will save the client_id and
client_secret for that configuration under ~/.jut/ and will generate access
tokens as needed. You can add multiple user accounts to your jut-tools local
setup so that you can easily swap between them when doing things on the
command line. 

### Using multiple configurations

If you have configured multiple configurations (ie `jut config add`) you can 
easily switch between them with a simple:

```
jut config defaults -u username
```

### Removing configurations

Removing a configuration is also very straightforward with:

```
jut config rm
```

And then follow the prompts to choose the correct configuration to remove.


## Jobs Command

### Check which jobs are running

To see the list of jobs currently running:

```
jut jobs list
```

### Kill a running job

You'll need to run `jut jobs list` to get the job id or possibly have a job id 
from persisting a job through the `jut run` command at which point you can kill
the running job like so:

```
jut jobs kill [your_job_id]
```

### Connect to a persistent job

When you start a persistent job you may find yourself wondering if its hitting
any errors or warnings and in order to check on it you can use the `jut jobs connect`
command to reconnect to a running job and snoop on the output. 

Lets say you were running a persistent program running 

```
jut run "read -type 'metric' name='cpu.idle' | reduce -every :hour: value=avg(value) | put name='cpu.idle.per.hour' | write -space 'collectd_rollups'" -p
dcee7afa
```

Notice we used the `-p` argument so that to persist the program and leave it
running. This specific program is calculating 5 minute average rollups for
`cpu.idle` metrics and writing them to our `collectd.rollup` space. Now lets say
we were wondering if the job with the id `dcee7afa` was writing out any warnings
or errors ? Well using the following we could snoop on the output like so:

```
jut jobs connect dcee7afa
```

And you'd now start seeing any error or warning messages. You won't see any 
data points since the program ended with a `write` sink. If you really wanted
to see points then you'd have to include a little debug trick like so in your
program:

```
read -type 'metric' name='cpu.idle' | reduce -every :hour: value=avg(value) | put name='cpu.idle.per.hour' | ( write -space 'collectd_rollups' ; pass)
```

So your program would end with a splitting of the stream where one of them goes
into a `write` while the other just passes through and pushes points back to a
client that maybe listening for data.


## Run Command

**jut** also allows you to easily run **juttle** from the command line and use
the results with the various other CLI tools you're use to using. Here are some
example uses:

### Getting JSON data out of Jut

Let's see how many points you ingested into the 'default' space in the last 5
minutes:

```
jut run "read -last :5 minutes: -space 'jut_internal' name='import.success' AND import_space='default' | reduce sum(value)"
```

Output:

```
[
{
    "sum": 24758
}
]
```

### Getting a list of things out of Jut

List of host names that have reported metrics to the 'collectd' space in the past minute

```
jut run -f text "read -space 'collectd' -last :1 minutes: | reduce count() by host | keep host | uniq host | sort host"
```

Output:

```
browses3
pypi
qa-selenium-node1
qa-selenium-node2
qa-selenium-node3
qa-selenium-node4
qa-selenium-node5
qa-selenium-node6
qa-selenium-node7
qa-selenium-node8
sauce0
```

### Reconstructing log lines from all your hosts with Jut

With the following you juttle you could easily put together all error log
lines in order from all of the systems currently sending their log lines to
your Jut instance:

```
jut run -f text "read -type 'event' -last :15 minutes: 'error' | keep time, message"
```

May look something like this:

```
2015-10-02T01:04:40.807Z _make_request error  getaddrinfo ENOTFOUND
2015-10-02T01:04:42.051Z Error obtaining access token: getaddrinfo ENOTFOUND
2015-10-02T01:04:48.413Z Error obtaining access token: getaddrinfo ENOTFOUND
2015-10-02T01:04:50.868Z ERROR [main] 2015-10-02 01:00:56,860 CassandraDaemon.java:202 - Directory /opt/jut/data/cassandra/commit_logs doesn't exist
2015-10-02T01:04:50.868Z ERROR [main] 2015-10-02 01:00:56,836 CassandraDaemon.java:202 - Directory /opt/jut/data/cassandra/data doesn't exist
2015-10-02T01:04:50.868Z ERROR [main] 2015-10-02 01:00:56,861 CassandraDaemon.java:202 - Directory /opt/jut/data/cassandra/cache doesn't exist
2015-10-02T01:04:50.870Z [2015-10-02 01:02:26,268][INFO ][cluster.metadata         ] [node-6b6002a5-8462-48de-a93d-c24dd0ffcb98] [events-jut_internal@2015.10.02] creating index, cause [auto(bulk api)], templates [schema-template-iis, schema-template-jira, schema-template-log4j, schema-template-github_push, schema-template-event, schema-template-jut_server, schema-template-github_commit, schema-template-jut_job_event, schema-template-jut_event, schema-template-cisco, schema-template-linux_logfile, schema-template-pagerduty, schema-template-ruby_logger, schema-template-jira_change, schema-template-syslog, schema-template-web_access, schema-template-web_error], shards [1]/[0], mappings [schema-iis, _default_, schema-jut_server, schema-syslog, schema-pagerduty, schema-jira_change, schema-jut_event, schema-jut_job_event, schema-log4j, schema-cisco, schema-linux_logfile, schema-event, schema-jira, schema-web_error, schema-github_commit, schema-web_access, schema-github_push, schema-ruby_logger]
2015-10-02T01:04:54.061Z Error obtaining access token: getaddrinfo ENOTFOUND
2015-10-02T01:05:00.056Z Error obtaining access token: getaddrinfo ENOTFOUND
2015-10-02T01:05:07.045Z _make_request error  getaddrinfo ENOTFOUND
2015-10-02T01:05:07.045Z Error obtaining access token: getaddrinfo ENOTFOUND
2015-10-02T01:05:10.702Z _make_request error  getaddrinfo ENOTFOUND
2015-10-02T01:05:10.702Z Error obtaining access token: getaddrinfo ENOTFOUND
2015-10-02T01:05:10.808Z Error obtaining access token: getaddrinfo ENOTFOUND
2015-10-02T01:05:10.808Z _make_request error  getaddrinfo ENOTFOUND
2015-10-02T01:05:11.708Z Error obtaining access token: getaddrinfo ENOTFOUND
2015-10-02T01:05:18.453Z Error obtaining access token: getaddrinfo ENOTFOUND
2015-10-02T01:05:18.960Z Error obtaining access token: getaddrinfo ENOTFOUND
2015-10-02T01:05:24.569Z (22846) error during import: Error: All connections on all I/O threads are busy
2015-10-02T01:05:24.570Z (22846) request 127.0.0.1 "POST /api/v1/import/default HTTP/1.1" 503 71 "-" "-" 110.375 ms
2015-10-02T01:05:24.571Z (22922) _make_request error  Received status code 503 from server.
```

### Getting a desktop notification with Jut

To get a desktop notification when any *collectd* CPU usage is higher than 90%
for over a minute, you could use something like so:

```
jut run "read -type 'metric' name='cpu.idle' | put value=100-value | reduce -every :1 minute: value=avg(value) | filter value > 90 | keep time, host, value"
```

Now the program is starting to get a little long so it may be best to simply
stick the program in a file like so:

```
read -type 'metric' name='cpu.idle'
| put value=100-value
| reduce -every :1 minute: value=avg(value)
| filter value > 90
| put message="${time}: CPU usage on host ${host} over 90% at ${value} for the past minute"
| keep message
```

Lets call it *collectd_cpu_alert.juttle* and then you can simply run this juttle
like so:

```
jut run examples/collectd_cpu_alert.juttle 
```

And with a desktop notification:

Try this first to test out the notification displays correctly

 * on linux:
   ```
   jut run -f text "emit -limit 1 | put message='Hello World'" | xargs -I {} notify-send 'Testing' '{}'
   ```

 * on mac:
   ```
   jut run -f text "emit -limit 1 | put message='Hello World'" | xargs -I {} osascript -e 'display notification "%" with title "Testing"'
   ```

Then you can run the high CPU usage juttle like so:

 * on linux:
   ```
   jut run -f text examples/collectd_cpu_alert.juttle | xargs notify-send "High CPU Usage" %
   ```

 * on mac:
   ```
   jut run -f text examples/collectd_cpu_alert.juttle | xargs osascript -e 'display notification "%" with title "High CPU Usage"' 
   ```

## Upload Command

### Upload a JSON file

To upload a JSON file containing multiple data points just use *jut* like
so:

```
jut upload data.json [-space some-other-space]
```

The above will simply upload the data points contained in the JSON file to 
the webhook connector listening on the default configuration.

You can also pipe JSON data to *jut* and it will handle uploading points
just fine:

```
curl 'https://api.github.com/repos/nodejs/node/issues?page=1&per_page=100&state=all' -o issues1.json | \
jut upload
```

Would upload those last 100 issues returned from the github issues API for the
*node* project.

Using `--dry-run` you can easily see what data you would have actually uploaded
and also how using additional options affects your data. Take for example the 
following simple JSON data:

```
[
  {
    "sha": "6908574bc2a0511084ee76f9e411bb9d",
    "name": "Rod The Dog",
    "email": "rod@jut.io",
    "date": "2015-08-28T06:24:29Z",
    "message": "Oh this is not going go well..."
  }
]
```

You could simply use `--dry-run` to see what the data would look like: 

```
> jut upload --dry-run                                                                        
POST: [
    {
        "date": "2015-08-28T06:24:29Z", 
        "sha": "6908574bc2a0511084ee76f9e411bb9d", 
        "message": "Oh this is not going go well...", 
        "name": "Rod The Dog", 
        "email": "rod@jut.io"
    }
]
```

Looking at that we realized we wanted to do a few things to our data points:

 1. remove the `email` field
 2. anonymize the `name` field
 3. rename `date` to the required `time` field

Luckily `jut` handles all of this with ease:

```
> jut upload data.json --dry-run \
  --remove-fields email --anonymize-fields name --rename-fields date=time
POST: [
    {
        "sha": "6908574bc2a0511084ee76f9e411bb9d", 
        "message": "Oh this is not going go well...", 
        "name": "0c33366cb1abf53c9200930210024b79", 
        "time": "2015-08-28T06:24:29Z"
    }
]
```
Removing the `--dry-run` and you'll push your data up to Jut in a jiffy.

### Uploading a directory of JSON files

Instead of building this type of feature into jut-tools we felt it was easier
for you to use your trusty command line tools like so:

```
for I in `ls *.json`
do
    jut upload $I
done
```

## Jut Python API
 
Bundled with the **jut-tools** is also the Jut Python API modules that you can 
use to easily interact with various Jut API's. The following sections will cover
a few examples of using the available modules.

### Auth API

The first thing you have to be able to do before you can interact with the Jut 
APIs is to authenticate with the Jut system. This can be easily done like so:

```python
from jut.apis import auth

token_manager = auth.TokenManager(username='john',password='doe')
```

The *token_manager* object can now be passed to various other APIs and will 
handle providing the necessary authentication tokens at runtime as well as
refreshing that token periodically as authentication tokens expire.

### Accounts API

The **Accounts API** is where you can create, delete and check details of an 
existing user. Here are a few examples of using the **Accounts API**:

```python
from jut.apis import auth, accounts

token_manager = auth.TokenManager(username='john',password='doe')

# create a new user
account_details = accounts.create_user('New Guy',
                                       'new',
                                       'newguy@company.com',
                                       'super-secret-password',
                                       token_manager=token_manager)

# delete an account (only user can delete him/herself)
accounts.delete_user('joe', token_manager=token_manager)
```

### Deployments API



### Data Engine API


## Development


### Running Tests

When developing there are some unittests that can be used to verify your
changes have not broken existing functionality as well as for you to add more
tests to verify your changes. To run these you need to supply a username/password
combo that has admin access to a real deployment. You can run it like so:

```
JUT_USER=username JUT_PASS=password python setup.py test
```

### Running a specific test

You can run just a test by name like so:

```
JUT_USER=username JUT_PASS=password python -m unittest tests.jut_upload_tests.JutUploadTests.test_jut_upload_to_url
```

Would run that one test within the upload tests called `test_jut_upload_to_url`
and if you wanted to run just the upload suite of tests then the invocation
would look like so:

```
JUT_USER=username JUT_PASS=password python -m unittest tests.jut_upload_tests
```
