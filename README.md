# jut-tools

Command line tools for interacting with your Jut instance.

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

## Configuration

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

## Usage Examples

### jut upload

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

### jut run

**jut** also allows you to easily run **juttle** from the command line and use
the results with the various other CLI tools you're use to using. Here are some
example uses:

#### see how many points you ingested into the 'default' space in the last 5 minutes

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

#### list of host names that have reported metrics to the 'collectd' space in the past minute

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

## Development

When developing there are some unittests that can be used to verify your
changes have not broken existing functionality as well as for you to add more
tests to verify your changes. To run these you need to supply a username/password
combo that has admin access to a real deployment. You can run it like so:

```
JUT_USER=username JUT_PASS=password python setup.py test
```

