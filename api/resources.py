import json
import requests
from dateutil.parser import parse as parse_timestamp

from api.exceptions import APIException
from sitegen.helpers import DateTimeEncoder
from sitegen.helpers import build_url


def discard_querystring(url):
    return url.split('?')[0]

def response_list_to_dict(responses):
    """
    Takes a list of HTTP responses as returned by grequests.map and creates a dict
    with the request url as the key and the response as the value. If the request
    was redirected (as shown by a history tuple on the response), the
    prior request url will be used as the key.
    """

    response_dict = {}
    if responses is None:
        return response_dict

    for response in responses:
        # Only follow one redirect. This is specifically to handle the /whoami
        # case where the client is redirected to /profiles/{id}
        if response.history:
            response_dict[discard_querystring(response.history[0].url)] = \
                APIResource.process_response(response.history[0].url, response)
        else:
            response_dict[discard_querystring(response.url)] = APIResource.process_response(response.url, response)
    return response_dict


class APIResource(object):
    """
    Base API resource that performs HTTP operations. Each API class should subclass this
    to deal with custom validation and JSON processing.
    """

    @staticmethod
    def process_response(url, response):
        try:
            resource = response.json()
        except ValueError:
            raise APIException('Response is not valid json:\n %s' % response.content, 500)
        if resource['error']:
            raise APIException(resource['error'], response.status_code)
        if resource['data'] is None:
            raise APIException('No data returned at: %s' % url)
        return resource['data']

    @staticmethod
    def make_request_headers(access_token=None):
        headers = {'Accept-Encoding': 'application/json'}
        if access_token:
            headers['Authorization'] = 'Bearer %s' % access_token
        return headers

    @staticmethod
    def retrieve(url, params, headers):
        """
        Fetch an API resource and handle any errors.
        """

        response = requests.get(url, params=params, headers=headers)
        return APIResource.process_response(url, response)

    @staticmethod
    def create(url, data, params, headers):
        """
        Create an API resource and handle any errors.
        """

        print 'Creating: ' + url
        headers['Content-Type'] = 'application/json'
        response = requests.post(url, data=data, params=params, headers=headers)
        return APIResource.process_response(url, response)

    @staticmethod
    def update(url, data, params, headers):
        """
        Update an API resource with PUT and handle any errors.
        """

        # Override HTTP method on API
        params['method'] = 'PUT'
        headers['Content-Type'] = 'application/json'
        response = requests.post(url, data=data, params=params, headers=headers)
        return APIResource.process_response(url, response)

    @staticmethod
    def delete(url, params, headers):
        """
        Delete an API resource. A 'data' object is never returned by a delete, so only
        raises an exception if 'error' is non-empty or the response cannot be parsed.
        """

        params['method'] = 'DELETE'
        response = requests.post(url, params=params, headers=headers)
        try:
            resource = response.json()
        except ValueError:
            raise APIException('The API has returned invalid json: %s' % response.content, 500)
        if resource['error']:
            raise APIException(resource['error'], response.status_code)


class Site(object):
    """
    Represents the current site (title, logo, etc.).
    """

    @classmethod
    def from_summary(cls, data):
        """
        For instantiating site objects in a list. Needs a better name.
        """

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data):
        site = Site()
        if data.get('siteId'): site.site_id = data['siteId']
        site.title = data['title']
        site.description = data['description']
        site.subdomain_key = data['subdomainKey']
        if data.get('ownedBy'): site.owned_by = Profile(data['ownedBy'])
        if data.get('domain'): site.domain = data['domain']
        if data.get('themeId'): site.theme_id = data['themeId']
        if data.get('logoUrl'): site.logo_url = data['logoUrl']
        if data.get('backgroundColor'): site.background_color = data['backgroundColor']
        if data.get('backgroundUrl'): site.background_url = data['backgroundUrl']
        if data.get('backgroundPosition'): site.background_position = data['backgroundPosition']
        if data.get('linkColor'): site.link_color = data['linkColor']
        if data.get('gaWebPropertyId'): site.ga_web_property_id = data['gaWebPropertyId']

        # auth configs are optional
        if data.get('auth0Domain'): site.auth0_domain = data['auth0Domain']
        if data.get('auth0ClientId'): site.auth0_client_id = data['auth0ClientId']

        return site

    @staticmethod
    def retrieve(host):
        url = build_url(host, ['site'])
        resource = APIResource.retrieve(url, {}, {})
        return Site.from_dict(resource)

    def create(self, host, access_token):
        url = build_url(host, ['sites'])
        payload = json.dumps(self.as_dict, cls=DateTimeEncoder)
        resource = APIResource.create(url, payload, {}, APIResource.make_request_headers(access_token))
        return Site.from_dict(resource)

    @staticmethod
    def update(host, site_id, data, access_token):
        url = build_url(host, ['sites', site_id])
        headers = APIResource.make_request_headers(access_token)
        resource = APIResource.update(url, json.dumps(data), {}, headers)
        return Site.from_dict(resource)

    @staticmethod
    def build_request(host, site_id, access_token):
        url = build_url(host, ['sites', site_id])
        headers = APIResource.make_request_headers(access_token)
        return url, {}, headers

    @property
    def as_dict(self):
        repr = {}
        if hasattr(self, 'id'):
            repr['id'] = self.site_id
        repr['title'] = self.title
        repr['description'] = self.description
        repr['subdomainKey'] = self.subdomain_key
        if hasattr(self, 'domain'):
            repr['domain'] = self.domain
        if hasattr(self, 'theme_id'):
            repr['themeId'] = self.theme_id
        if hasattr(self, 'logoUrl'):
            repr['logoUrl'] = self.logo
        if hasattr(self, 'backgroundUrl'):
            repr['backgroundUrl'] = self.header_background_url
        if hasattr(self, 'backgroundColor'):
            repr['backgroundColour'] = self.header_background_colour
        if hasattr(self, 'backgroundPosition'):
            repr['backgroundPosition'] = self.header_background_colour
        if hasattr(self, 'linkColor'):
            repr['linkColor'] = self.linkColor
        if hasattr(self, 'gaWebPropertyId'):
            repr['gaWebPropertyId'] = self.ga_web_property_id
        if hasattr(self, 'auth0Domain'):
            repr['auth0Domain'] = self.auth0_domain
        if hasattr(self, 'auth0ClientId'):
            repr['auth0ClientId'] = self.auth0_client_id
        return repr


class SiteList(object):

    api_path_fragment = 'sites'

    def __init__(self, data):
        self.sites = PaginatedList(data['sites'], Site)
        self.meta = Meta(data['meta'])

    @staticmethod
    def build_request(host, offset=None, access_token=None):
        url = build_url(host, [SiteList.api_path_fragment])
        params = {
            'offset': offset if offset else {},
            'filter': 'owned',
        }
        headers = APIResource.make_request_headers(access_token)
        return url, params, headers

    @staticmethod
    def retrieve(host, offset=None, access_token=None):
        url, params, headers = SiteList.build_request(host, offset, access_token)
        resource = APIResource.retrieve(url, params, headers)
        return SiteList(resource)


class User(object):
    """
    User API resource. A user is only defined once across the platform
    (and is thus multi-site). A Profile is site specific, and associates
    a given user and site.
    """

    api_path_fragment = 'users'

    def __init__(self, data):
        self.email = data['email']

    @staticmethod
    def retrieve(host, id, access_token):
        url = build_url(host, [User.api_path_fragment, id])
        resource = APIResource.retrieve(url, {}, APIResource.make_request_headers(access_token))
        return User(resource)


class WhoAmI(object):
    """
    WhoAmI returns the profile of the currently logged-in user.
    """

    api_path_fragment = 'whoami'

    @staticmethod
    def build_request(host, access_token):
        url = build_url(host, [WhoAmI.api_path_fragment])
        params = {}
        headers = APIResource.make_request_headers(access_token)
        return url, params, headers

    @staticmethod
    def retrieve(host, access_token):
        url, params, headers = WhoAmI.build_request(host, access_token)
        resource = APIResource.retrieve(url, params=params, headers=headers)
        return Profile(resource)


class Profile(object):
    """
    Represents a user profile belonging to a specific site.
    """

    api_path_fragment = 'profiles'

    def __init__(self, data, summary=True):
        """
        We're permissive about the data passed in, since it may
        be a PUT or PATCH operation and not have all the expected keys.
        """

        if data.get('id'): self.id = data['id']
        if data.get('siteId'): self.site_id = data['siteId']
        if data.get('userId'): self.user_id = data['userId']
        if data.get('email'): self.email = data['email']
        if data.get('profileName'): self.profile_name = data['profileName']
        if data.get('visible'): self.visible = data['visible']
        if data.get('avatar'): self.avatar = data['avatar']
        if data.get('meta'): self.meta = Meta(data['meta'])

        if not summary:
            self.style_id = data['styleId']
            self.item_count = data['itemCount']
            self.comment_count = data['commentCount']
            self.created = parse_timestamp(data['created'])
            self.last_active = parse_timestamp(data['lastActive'])

    @classmethod
    def from_summary(cls, data):
        profile = Profile(data, summary=True)
        return profile

    @staticmethod
    def retrieve(host, id, access_token=None):
        url = build_url(host, [Profile.api_path_fragment, id])
        resource = APIResource.retrieve(url, {}, APIResource.make_request_headers(access_token))
        return Profile(resource, summary=False)

    def update(self, host, access_token):
        url = build_url(host, [Profile.api_path_fragment, self.id])
        payload = json.dumps(self.as_dict, cls=DateTimeEncoder)
        resource = APIResource.update(url, payload, {}, APIResource.make_request_headers(access_token))
        return Profile(resource, summary=False)

    @property
    def as_dict(self):
        repr = {}
        if hasattr(self, 'id'): repr['id'] = self.id
        if hasattr(self, 'site_id'): repr['siteId'] = self.site_id
        if hasattr(self, 'user_id'): repr['userId'] = self.user_id
        if hasattr(self, 'profile_name'): repr['profileName'] = self.profile_name
        if hasattr(self, 'visible'): repr['visible'] =  self.visible
        if hasattr(self, 'avatar'): repr['avatar'] = self.avatar
        if hasattr(self, 'style_id'): repr['styleId'] = self.style_id
        if hasattr(self, 'item_count'): repr['itemCount'] = self.item_count
        if hasattr(self, 'comment_count'): repr['commentCount'] = self.comment_count
        if hasattr(self, 'created'): repr['created'] = self.created
        if hasattr(self, 'last_active'): repr['lastActive'] = self.last_active
        if hasattr(self, 'banned'): repr['banned'] = self.banned
        if hasattr(self, 'admin'): repr['admin'] = self.admin
        return repr

    @staticmethod
    def get_unread_count(host, access_token):
        url = build_url(host, ['updates', 'unread'])
        return APIResource.retrieve(url, {}, headers=APIResource.make_request_headers(access_token))


class PaginatedList(object):
    """
    Generic list of items and pagination metadata (total, number of pages, etc.).
    """

    def __init__(self, item_list, list_item_cls):
        self.total = item_list['total']
        self.limit = item_list['limit']
        self.offset = item_list['offset']
        self.max_offset = item_list['maxOffset']
        self.total_pages = item_list['totalPages']
        self.page = item_list['page']
        self.type = item_list['type']
        if item_list.get('items'):
            self.items = [list_item_cls.from_summary(item) for item in item_list['items']]
        self.links = {}
        for item in item_list['links']:
            if 'title' in item:
                self.links[item['rel']] = {'href': item['href'], 'title': item['title']}
            else:
                self.links[item['rel']] = {'href': item['href']}


class Meta(object):
    """
    Represents a resource 'meta' type, including creation time/user,
    flags, links, and permissions.
    """

    def __init__(self, data):
        if data.get('created'): self.created = (parse_timestamp(data['created']))
        if data.get('createdBy'): self.created_by = Profile(data['createdBy'])
        if data.get('edited'): self.edited = (parse_timestamp(data['edited']))
        if data.get('editedBy'): self.edited_by = Profile(data['editedBy'])
        if data.get('flags'): self.flags = data['flags']
        if data.get('permissions'): self.permissions = PermissionSet(data['permissions'])
        if data.get('links'):
            self.links = {}
            for item in data['links']:
                if 'title' in item:
                    self.links[item['rel']] = {'href': str.replace(str(item['href']),'/api/v1',''), 'title': item['title']}
                else:
                    self.links[item['rel']] = {'href': str.replace(str(item['href']),'/api/v1','')}


class PermissionSet(object):
    """
    Represents user permissions on a resource.
    """

    def __init__(self, data):
        self.create = data['create']
        self.read = data['read']
        self.update = data['update']
        self.delete = data['delete']
        self.guest = data['guest']
        self.super_user = data['moderator']


class FileMetadata(object):
    """
    For managing user-uploaded files.
    TODO: manage multiple uploads
    """

    api_path_fragment = 'files'

    @classmethod
    def from_create_form(cls, file_upload):
        file_metadata = cls()
        file_metadata.file = {file_upload.name: file_upload.read()}
        return file_metadata

    @classmethod
    def from_api_response(cls, data):
        file_metadata = cls()
        file_metadata.created = parse_timestamp(data[0]['created'])
        file_metadata.file_size = data[0]['fileSize']
        file_metadata.file_hash = data[0]['fileHash']
        file_metadata.mime_type = data[0]['mimeType']
        if data[0].get('fileExt'):
            file_metadata.file_ext = data[0]['fileExt']
        return file_metadata

    def create(self, host, access_token, width=0, height=0):
        url = 'https://' + host + '/api/v1/files'
        print 'making req: ' + url
        if height > 0 or width > 0:
            url += "?maxWidth=" + str(width) + "&maxHeight=" + str(height)
        headers = APIResource.make_request_headers(access_token)
        response = APIResource.process_response(url, requests.post(url, files=self.file, headers=headers))
        return FileMetadata.from_api_response(response)

class Legal(APIResource):
    """
    Represents /legal/document
    """

    api_path_fragment = 'legal'

    @classmethod
    def from_api_response(cls, data):
        legal = cls()

        if data.get('link'):
            legal.link = data['link']
        if data.get('html'):
            legal.html = data['html']

        return legal

    @staticmethod
    def build_request(host, doc = '', access_token=None):
        url = build_url(host, [Legal.api_path_fragment, doc])
        headers = APIResource.make_request_headers(access_token)
        return url, {}, headers

    @staticmethod
    def retrieve(host, offset=None, access_token=None):
        url, params, headers = Microcosm.build_request(host, offset, access_token)
        resource = APIResource.retrieve(url, params, headers)
        return Legal.from_api_response(resource)
