import random
import string
import json
import os

from django.utils import unittest

from api.resources import Profile
from api.resources import Site

from sitegen.helpers import build_url

from sitegen.settings import API_SCHEME
from sitegen.settings import API_DOMAIN_NAME
from sitegen.settings import API_PATH
from sitegen.settings import API_VERSION

TEST_ROOT = os.path.dirname(os.path.abspath(__file__))


def generate_location():
    # Construct a random subdomain string
    subdomain = ''
    for x in xrange(10):
        subdomain += random.choice(string.lowercase)
    return '%s.microco.sm' % subdomain


class BuildURLTests(unittest.TestCase):
    """
    Verify that helpers.build_url() builds valid URLs.
    """

    def testWithTrailingSeparator(self):
        url = build_url(API_DOMAIN_NAME, ['resource/', '1/', 'extra/'])
        assert url == API_SCHEME + \
                      API_DOMAIN_NAME + '/' + API_PATH + '/' + API_VERSION + '/resource/1/extra'

    def testWithPrependedSeparator(self):
        url = build_url(API_DOMAIN_NAME, ['/resource', '/1', '/extra'])
        assert url == API_SCHEME + \
                      API_DOMAIN_NAME + '/' + API_PATH + '/' + API_VERSION + '/resource/1/extra'

    def testWithDuplicateSeparator(self):
        url = build_url(API_DOMAIN_NAME, ['resource/', '/1/', '/extra/'])
        assert url == API_SCHEME + \
                      API_DOMAIN_NAME + '/' + API_PATH + '/' + API_VERSION + '/resource/1/extra'

    def testWithNoSeparator(self):
        url = build_url(API_DOMAIN_NAME, ['resource', '1', 'extra'])
        assert url == API_SCHEME + \
                      API_DOMAIN_NAME + '/' + API_PATH + '/' + API_VERSION + '/resource/1/extra'

    def testEmptyFragments(self):
        url = build_url(API_DOMAIN_NAME, [])
        assert url == API_SCHEME + \
                      API_DOMAIN_NAME + '/' + API_PATH + '/' + API_VERSION

    def testIntFragment(self):
        url = build_url(API_DOMAIN_NAME, [1, 2, 3])
        assert url == API_SCHEME + \
                      API_DOMAIN_NAME + '/' + API_PATH + '/' + API_VERSION + '/1/2/3'

    def testInvalidFragment(self):
        with self.assertRaises(AssertionError):
            build_url(API_DOMAIN_NAME, ['resource', '1', 'ex/tra'])


class ResourceTests(unittest.TestCase):

    """
    Basic initialisation and serilisation tests for API resources.
    """

    def testProfileInit(self):
        Profile(json.loads(open(os.path.join(TEST_ROOT, 'data', 'profile.json')).read())['data'])

    def testProfileAsDict(self):
        profile = Profile(json.loads(open(os.path.join(TEST_ROOT, 'data', 'profile.json')).read())['data'])
        profile.as_dict

    def testProfileSummaryInit(self):
        Profile(json.loads(open(os.path.join(TEST_ROOT, 'data', 'profile.json')).read())['data'], summary=True)

    def testSiteInit(self):
        Site(json.loads(open(os.path.join(TEST_ROOT, 'data', 'site.json')).read())['data'])
