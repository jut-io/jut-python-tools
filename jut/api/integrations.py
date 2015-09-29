"""
jut integrations api

"""

from jut import defaults

from jut.api import deployments, data_engine


def get_webhook_url(deployment_name,
                    space='default',
                    data_source='webhook',
                    access_token=None,
                    app_url=defaults.APP_URL,
                    **fields):
    """

    """

    import_url = data_engine.get_import_data_url(deployment_name,
                                                 app_url=app_url,
                                                 access_token=access_token)

    api_key = deployments.get_apikey(deployment_name,
                                     access_token=access_token,
                                     app_url=app_url)

    fields_string = '&'.join(['%s=%s' % (key, value)
                              for (key, value) in fields.items()])
    return '%s/api/v1/import/webhook/?space=%s&data_source=%sk&apikey=%s&%s' % \
           (import_url, space, data_source, api_key, fields_string)


