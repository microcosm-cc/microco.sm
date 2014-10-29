import datetime
import logging
import requests

from requests import RequestException

import grequests
import newrelic

from django.conf import settings
from django.http import HttpResponseNotFound
from django.http import HttpResponseForbidden
from django.http import HttpResponseServerError
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import redirect
from django.template import RequestContext
from django.template import loader
from django.views.generic.base import RedirectView
from django.views.generic.base import TemplateView
from django.views.decorators.http import require_http_methods

from api.resources import response_list_to_dict
from api.resources import Profile
from api.resources import WhoAmI
from api.resources import Site

from api.exceptions import APIException

from sitegen.helpers import build_url

logger = logging.getLogger('core.views')


class ProfileView(object):
    single_template = 'profile.html'

    @staticmethod
    def single(request, profile_id):
        """
        Display a single profile by ID.
        """

        responses = response_list_to_dict(grequests.map(request.view_requests))
        view_data = {
            'user': Profile(responses[request.whoami_url], summary=False) if request.whoami_url else None,
            'site': request.site
        }

        profile = Profile.retrieve(request.META['HTTP_HOST'], profile_id, request.access_token)

        view_data['content'] = profile

        return render(request, ProfileView.single_template, view_data)


class ErrorView(object):
    @staticmethod
    def not_found(request):
        view_data = {}
        view_requests = []

        if request.COOKIES.has_key('access_token'):
            request.access_token = request.COOKIES['access_token']
            whoami_url, params, headers = WhoAmI.build_request(request.get_host(), request.access_token)
            view_requests.append(grequests.get(whoami_url, params=params, headers=headers))

        responses = response_list_to_dict(grequests.map(view_requests))
        if request.whoami_url:
            profile = Profile(responses[whoami_url], summary=False)
            view_data['user'] = profile
            newrelic.agent.add_custom_parameter('profile_name', profile.profile_name)
            newrelic.agent.add_custom_parameter('profile_id', profile.id)
            newrelic.agent.add_custom_parameter('user_id', profile.user_id)

        context = RequestContext(request, view_data)
        return HttpResponseNotFound(loader.get_template('404.html').render(context))

    @staticmethod
    def forbidden(request):
        view_data = {}
        view_requests = []

        if request.COOKIES.has_key('access_token'):
            request.access_token = request.COOKIES['access_token']
            whoami_url, params, headers = WhoAmI.build_request(request.get_host(), request.access_token)
            view_requests.append(grequests.get(whoami_url, params=params, headers=headers))

        responses = response_list_to_dict(grequests.map(view_requests))
        if request.whoami_url:
            profile = Profile(responses[whoami_url], summary=False)
            view_data['user'] = profile
            newrelic.agent.add_custom_parameter('profile_name', profile.profile_name)
            newrelic.agent.add_custom_parameter('profile_id', profile.id)
            newrelic.agent.add_custom_parameter('user_id', profile.user_id)

        context = RequestContext(request, view_data)
        return HttpResponseForbidden(loader.get_template('403.html').render(context))

    @staticmethod
    def server_error(request):
        view_data = {}
        view_requests = []

        if request.COOKIES.has_key('access_token'):
            request.access_token = request.COOKIES['access_token']
            whoami_url, params, headers = WhoAmI.build_request(request.get_host(), request.access_token)
            view_requests.append(grequests.get(whoami_url, params=params, headers=headers))

        responses = response_list_to_dict(grequests.map(view_requests))
        if request.whoami_url:
            profile = Profile(responses[whoami_url], summary=False)
            view_data['user'] = profile
            newrelic.agent.add_custom_parameter('profile_name', profile.profile_name)
            newrelic.agent.add_custom_parameter('profile_id', profile.id)
            newrelic.agent.add_custom_parameter('user_id', profile.user_id)

        context = RequestContext(request, view_data)
        return HttpResponseServerError(loader.get_template('500.html').render(context))

    @staticmethod
    def requires_login(request):
        view_data = {}
        view_data['logout'] = True

        context = RequestContext(request, view_data)
        return HttpResponseForbidden(loader.get_template('403.html').render(context))


class AuthenticationView(object):
    @staticmethod
    def login(request):
        """
        Log a user in. Creates an access_token using a persona
        assertion and the client secret. Sets this access token as a cookie.
        'target_url' based as a GET parameter determines where the user is
        redirected.
        """

        target_url = request.POST.get('target_url')
        assertion = request.POST.get('Assertion')
        postdata = {
            'Assertion': assertion,
            'ClientSecret': settings.CLIENT_SECRET
        }

        url = build_url(request.get_host(), ['auth'])
        try:
            response = requests.post(url, data=postdata, headers={})
        except RequestException:
            return ErrorView.server_error(request)
        access_token = response.json()['data']
        if access_token is None:
            return ErrorView.server_error(request)

        response = HttpResponseRedirect(target_url if target_url != '' else '/')
        expires = datetime.datetime.fromtimestamp(2 ** 31 - 1)
        response.set_cookie('access_token', access_token, expires=expires, httponly=True)
        return response

    @staticmethod
    @require_http_methods(['POST', ])
    def logout(request):
        """
        Log a user out. Issues a DELETE request to the backend for the
        user's access_token, and issues a delete cookie header in response to
        clear the user's access_token cookie.
        """

        response = redirect('/')
        if request.COOKIES.has_key('access_token'):
            response.set_cookie('access_token', '', expires="Thu, 01 Jan 1970 00:00:00 GMT")
            url = build_url(request.get_host(), ['auth', request.access_token])
            try:
                requests.post(url, params={'method': 'DELETE', 'access_token': request.access_token})
            except RequestException:
                return ErrorView.server_error(request)

        return response


def respond_with_error(request, exception):
    if not isinstance(exception, APIException):
        logger.error(str(exception))
        return ErrorView.server_error(request)

    if exception.status_code == 404:
        return ErrorView.not_found(request)
    elif exception.status_code == 403:
        return ErrorView.forbidden(request)
    elif exception.status_code == 401:
        return ErrorView.requires_login(request)
    else:
        return ErrorView.server_error(request)


def echo_headers(request):
    view_data = '<html><body><table>'
    for key in request.META.keys():
        view_data += '<tr><td>%s</td><td>%s</td></tr>' % (key, request.META[key])
    view_data += '</table></body></html>'
    return HttpResponse(view_data, content_type='text/html')


class FaviconView(RedirectView):
    def get_redirect_url(self, **kwargs):
        return settings.STATIC_URL + '/img/favico.png'


class RobotsView(TemplateView):
    template_name = 'robots.txt'
    content_type = 'text/plain'

    def get_context_data(self, **kwargs):
        return super(RobotsView, self).get_context_data(**kwargs)
