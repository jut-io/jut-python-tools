"""
jut integrations api

"""

from jut import defaults

from jut.api import deployments, data_engine


def get_webhook_url(deployment_name,
                    space='default',
                    data_source='webhook',
                    token_manager=None,
                    app_url=defaults.APP_URL,
                    **fields):
    """
    return the webhook URL for posting webhook data to

    """

    import_url = data_engine.get_import_data_url(deployment_name,
                                                 app_url=app_url,
                                                 token_manager=token_manager)

    api_key = deployments.get_apikey(deployment_name,
                                     token_manager=token_manager,
                                     app_url=app_url)

    fields_string = '&'.join(['%s=%s' % (key, value)
                              for (key, value) in fields.items()])
    return '%s/api/v1/import/webhook/?space=%s&data_source=%sk&apikey=%s&%s' % \
           (import_url, space, data_source, api_key, fields_string)


