"""
rest_api - defines the basic capabilities of the Confluence Cloud REST API

These are "raw" capabilities, and will be wrapped by "prettier" functions
"""
from confluence_cloud import mlog, _DETAILED_DEBUG
from confluence_cloud.utils import str_nocase_equal, thin_dict

import requests

from pprint import pformat


class ConfluenceCloudClient(object):
    DEFAULT_RESULTS_LIMIT = 100

    def __init__(self, base_url, auth,
                 request_options={},
                 api_base='/wiki/rest/api'):
        """
        Creates new connection to Confluence Cloud REST API at a given domain

        ::example

            client = ConfluenceCloudClient('https://myacconunt.atlassian.net',
                                           auth=api_token_from_file('apitoken.secret'))

        :param base_url: your account base URL
        :param auth: a tuple/list containing your id and API access token
        :param request_options: options (k/v) to pass to each Requests call
        :param api_base: alternative path to the API, added to base_url for API calls
        """
        self.apiurl = base_url + api_base
        mlog.debug(f"API URL '{self.apiurl}'")
        # self.apiurl.replace('//', '/')  # remove all double-slash constructs
        self.requests_options = request_options

        # set up requests session with auth token and options
        self.session = requests.Session()
        self.session.auth = tuple(auth)
        self.session.headers.update({
            'X-Atlassian-Token': 'no-check',  # tells anti-XSS this is a legit call not a clicked link
            'Accept': 'application/json',  # by default, return JSON data structures
        })
        mlog.debug(f"Session headers: {self.session.headers}")

        # enumerate current user - verifies login and gets accountId and attributes for other calls
        self.user = self.current_user()
        mlog.info(f"Established conenction to '{self.apiurl}' as user {self.user['accountId']}" +
                  f" = \"{self.user['displayName']}\" <{self.user['email']}>")

    def _api_call(self, verb, query, query_params=None, query_args=None, data=None, json=None, **request_options):
        # First, build a dict of kwargs that will be past to the request, combining the field and the arugment
        request_kwargs = self.requests_options.copy()
        for k in request_options.keys():
            request_kwargs[k] = request_options[k]

        # Now build the URL from query and query_params
        request_url = self.apiurl + query
        if query_params is not None:
            request_url = request_url.format(**query_params)  # TODO maybe URL_encode the params here?

        mlog.debug(f"Call '{verb} {request_url}' with params {query_args} using {request_kwargs}")

        # perform the action for the verb and request URL
        if str_nocase_equal('GET', verb):
            response = self.session.get(request_url, params=query_args, **request_kwargs)
        elif str_nocase_equal('POST', verb):
            response = self.session.post(request_url, params=query_args, data=data, json=json, **request_kwargs)
        elif str_nocase_equal('PUT', verb):
            response = self.session.put(request_url, params=query_args, data=data, json=json, **request_kwargs)
        elif str_nocase_equal('DELETE', verb):
            response = self.session.delete(request_url, **request_kwargs)
        else:
            raise ValueError(f"Invalide verb '{verb}'")

        mlog.debug(f"{response.request.method} {response.request.path_url} {response.request.headers} {response.request.body}")

        # raise an error if the status isn't OK
        response.raise_for_status()
        return response  # the caller has to figure out whether to use response.content or response.json or whatev

    @property
    def personalSpaceKey(self):
        if self.user is None:
            self.user = self.current_user()
        return self.user['personalSpace']['key']

    def content_update_base(self, old_content=None):
        """
        prepares an update dict for updating content, optionally based on old content

        If an ``old_content`` dict is provided, then:
        * Title, and Type are pre-populated with its values
        * Version is read from old content and incremented

        :param old_content:
        :return: a dict that can be passed to ``update_content``
        """
        base = {
            'version': {'number': 1},
            'title': None,
            'type': 'page',
            'body': {'storage': {'value': "", 'representation': 'storage'}}
        }

        if old_content is None:
            return base

        base['title'] = old_content['title']
        base['type'] = old_content['type']
        base['version']['number'] = old_content['version']['number'] + 1

        return base

    def current_user(self, expand='details.personal,details.business,personalSpace,operations'):
        # TODO is current_user worth caching?
        mlog.debug(f"Requesting current user, expand='{expand}'")
        response = self._api_call('GET', '/user/current', query_args={'expand': expand})
        return response.json()

    # TODO do I need spaces?
    def spaces(self, space_keys=None,
               start=0, limit=DEFAULT_RESULTS_LIMIT):
        response = self._api_call('GET', '/space',
                                  query_args={
                                      'spaceKeys': space_keys,
                                      'start': start,
                                      'limit': limit
                                  })
        return response.json()

    def pages(self, title, space=None, status=None, date=None, mark_visited=False, order_by=None,
              start=0, limit=DEFAULT_RESULTS_LIMIT, expand='space,history,version,metadata', also_expand=None):
        if also_expand is not None:
            expand += ',' + also_expand

        query_args = thin_dict({
            'type': 'page',  # immutable -- that's how we return only pages
            'title': title,
            'spaceKey': space,
            'status': status,
            'postingDay': date,
            'trigger': 'visited' if mark_visited else None,
            'orderby': order_by,
            'start': start,
            'limit': limit,
            'expand': expand
        })
        mlog.debug(f"Pages request, query args: {query_args}")

        response = self._api_call('GET', '/content', query_args=query_args)
        data = response.json()
        _DETAILED_DEBUG and mlog.debug(f"Response {data}")
        return data

    def content_byid(self, contentid, expand='space,history,version', also_expand=None):
        if also_expand is not None:
            expand += ',' + also_expand

        response = self._api_call('GET', '/content/{id}', query_params={'id': contentid},
                                  query_args=thin_dict({'expand': expand}))
        data = response.json()
        _DETAILED_DEBUG and mlog.debug(f"Response {data}")
        return data

    def update_content(self, contentid, updates, status='current', on_conflict='abort'):
        response = self._api_call('PUT', '/content/{id}', {'id': contentid},
                                  query_args=thin_dict({'status': status, 'conflictPolicy': on_conflict}),
                                  json=updates)
        data = response.json()
        _DETAILED_DEBUG and mlog.debug(f"Response {data}")
        return data

    def create_page(self, title, space, body='', ancestor_id=None):
        page_data = {
            'title': title,
            'space': {'key': space},
            'type': 'page',
            'status': 'current',
            'body': {'storage': {'representation': 'storage', 'value': body}}
        }

        if ancestor_id is not None:
            page_data['ancestors'] = {'id': ancestor_id}

        mlog.debug(f"Create page data: {page_data}")

        response = self._api_call('POST', '/content', json=page_data)
        json_response = response.json()
        mlog.info(f"created page id {json_response['id']}: \"{json_response['title']}\"")
        mlog.debug(json_response)
        return response.json()['id']
