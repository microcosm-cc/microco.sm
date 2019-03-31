import grequests

import re

from django.core.urlresolvers import reverse
from django.shortcuts import render

from api.resources import response_list_to_dict
from api.resources import Profile
from api.resources import Legal

from api.exceptions import APIException

from core.views import respond_with_error


class LandingView():
    @staticmethod
    def index(request):

        regex_http_          = re.compile(r'^HTTP_.+$')
        regex_content_type   = re.compile(r'^CONTENT_TYPE$')
        regex_content_length = re.compile(r'^CONTENT_LENGTH$')

        request_headers = {}
        for header in request.META:
            if regex_http_.match(header) or regex_content_type.match(header) or regex_content_length.match(header):
                request_headers[header] = request.META[header]

        try:
            responses = response_list_to_dict(grequests.map(request.view_requests))
        except APIException as exc:
            return respond_with_error(request, exc)

        view_data = {
            'site': request.site,
            'user': Profile(responses[request.whoami_url], summary=False) if request.whoami_url else None,
            'login_target': reverse('dashboard-sites'),
            'headers': request_headers
        }
        return render(request, 'index.html', view_data)


class AboutView():
    template = 'about.html'

    @staticmethod
    def index(request):
        try:
            responses = response_list_to_dict(grequests.map(request.view_requests))
        except APIException as exc:
            return respond_with_error(request, exc)
        view_data = {
            'user': Profile(responses[request.whoami_url], summary=False) if request.whoami_url else None,
            'site': request.site,
        }
        return render(request, AboutView.template, view_data)


class FaqsView():
    template = 'faqs.html'

    @staticmethod
    def index(request):
        try:
            responses = response_list_to_dict(grequests.map(request.view_requests))
        except APIException as exc:
            return respond_with_error(request, exc)
        view_data = {
            'user': Profile(responses[request.whoami_url], summary=False) if request.whoami_url else None,
            'site': request.site,
        }
        return render(request, FaqsView.template, view_data)


class CompareView():
    template = 'compare.html'

    @staticmethod
    def index(request):
        try:
            responses = response_list_to_dict(grequests.map(request.view_requests))
        except APIException as exc:
            return respond_with_error(request, exc)
        view_data = {
            'user': Profile(responses[request.whoami_url], summary=False) if request.whoami_url else None,
            'site': request.site,
        }
        return render(request, CompareView.template, view_data)


class DevelopersView():
    template = 'developers.html'

    @staticmethod
    def index(request):
        try:
            responses = response_list_to_dict(grequests.map(request.view_requests))
        except APIException as exc:
            return respond_with_error(request, exc)
        view_data = {
            'user': Profile(responses[request.whoami_url], summary=False) if request.whoami_url else None,
            'site': request.site,
        }
        return render(request, DevelopersView.template, view_data)


class LegalView():
    template_terms = 'terms.html'
    template_privacy = 'privacy.html'

    @staticmethod
    def terms(request):
        url, params, headers = Legal.build_request(
            request.META['HTTP_HOST'],
            doc='service',
        )
        request.view_requests.append(grequests.get(url, params=params, headers=headers))

        try:
            responses = response_list_to_dict(grequests.map(request.view_requests))
        except APIException as exc:
            return respond_with_error(request, exc)

        legal = Legal.from_api_response(responses[url])

        view_data = {
            'user': Profile(responses[request.whoami_url], summary=False) if request.whoami_url else None,
            'content': legal,
            'site': request.site,
        }
        return render(request, LegalView.template_terms, view_data)


class FeaturesView():
    template = 'features.html'

    @staticmethod
    def index(request):
        try:
            responses = response_list_to_dict(grequests.map(request.view_requests))
        except APIException as exc:
            return respond_with_error(request, exc)
        view_data = {
            'user': Profile(responses[request.whoami_url], summary=False) if request.whoami_url else None,
            'site': request.site,
        }
        return render(request, FeaturesView.template, view_data)
