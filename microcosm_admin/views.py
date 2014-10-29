from django.core.urlresolvers import reverse
from django.http.response import HttpResponseNotFound
import grequests

from django.http import HttpResponseRedirect
from django.shortcuts import render
from api.exceptions import APIException

from api.resources import Site
from api.resources import SiteList
from api.resources import Profile
from api.resources import FileMetadata
from api.resources import response_list_to_dict
from api.utils import build_pagination_links

from core.views import respond_with_error

import logging

logger = logging.getLogger('admin.views')

default_logo = 'https://meta.microco.sm/static/themes/1/logo.png'


class HomeView():
    template = 'index.html'

    @staticmethod
    def index(request):
        return render(request, HomeView.template)


class SitesView():
    template_list = 'site-list.html'
    template_create = 'site-create.html'
    template_edit = 'site-edit.html'

    @staticmethod
    def list(request):

        """
        Display a list of the user's sites or an empty state.
        """

        if request.access_token is None:
            return HttpResponseRedirect(reverse('site-home'))

        try:
            offset = int(request.GET.get('offset', 0))
        except ValueError:
            offset = 0

        sites_url, params, headers = SiteList.build_request(request.META['HTTP_HOST'], offset=offset,
            access_token=request.access_token)

        request.view_requests.append(grequests.get(sites_url, params=params, headers=headers))

        try:
            responses = response_list_to_dict(grequests.map(request.view_requests))
        except APIException as exc:
            return respond_with_error(request, exc)

        sites = SiteList(responses[sites_url])

        view_data = {
            'user': Profile(responses[request.whoami_url], summary=False) if request.whoami_url else None,
            'site': request.site,
            'content': sites,
            'pagination': build_pagination_links(responses[sites_url]['sites']['links'], sites.sites)
        }
        return render(request, SitesView.template_list, view_data)

    @staticmethod
    def create(request):
        if request.method == 'GET':
            try:
                responses = response_list_to_dict(grequests.map(request.view_requests))
            except APIException as exc:
                return respond_with_error(request, exc)
            view_data = {
                'user': Profile(responses[request.whoami_url], summary=False) if request.whoami_url else None,
                'site': request.site,
                'site_name': request.GET['name'] if request.GET.get('name') else None
            }
            return render(request, SitesView.template_create, view_data)

        if request.method == 'POST':
            try:
                responses = response_list_to_dict(grequests.map(request.view_requests))
            except APIException as exc:
                return respond_with_error(request, exc)
            view_data = {
                'user': Profile(responses[request.whoami_url], summary=False) if request.whoami_url else None,
                'site': request.site,
            }

            # Request from landing page
            if request.POST.get('new_site_name'):
                view_data['site_name'] = request.POST['new_site_name']
                return render(request, SitesView.template_create, view_data)

            # Not from landing page, assume user is logged in and create the site.
            new_site_data = {
                'title': request.POST['site_name'],
                'description': request.POST['site_description'],
                'subdomainKey': request.POST['site_subdomain'],
            }
            site_request = Site.from_dict(new_site_data)
            try:
                site_request.create(request.META['HTTP_HOST'], request.access_token)
            except APIException as exc:
                return respond_with_error(request, exc)
            return HttpResponseRedirect(reverse('dashboard-sites'))

    @staticmethod
    def edit(request, site_id):
        if request.access_token is None:
            return HttpResponseRedirect(reverse('site-home'))

        if request.POST:
            if request.POST.has_key('site_name'):
                payload = {
                    'title': request.POST.get('site_name'),
                    'description': request.POST.get('site_description')
                }
                if request.POST.get('reset_logo'):
                    payload['logoUrl'] = default_logo
                elif request.FILES.has_key('logo'):
                    file_request = FileMetadata.from_create_form(request.FILES['logo'])
                    try:
                        metadata = file_request.create((request.POST['site_subdomain_key'] + '.microco.sm'),
                            request.access_token, width=240, height=89)
                    except APIException as exc:
                        return respond_with_error(request, exc)
                    logo_url = 'https://' + request.POST['site_subdomain_key'] + '.microco.sm/api/v1/files/' + metadata.file_hash
                    if hasattr(metadata, 'file_ext'):
                        logo_url = logo_url + '.' + metadata.file_ext
                    payload['logoUrl'] = logo_url

            if request.POST.has_key('bg_color'):
                payload = {
                    'backgroundPosition': request.POST.get('bg_position'),
                    'backgroundColor': request.POST.get('bg_color'),
                    'linkColor': request.POST.get('link_color'),
                }
                if request.POST.get('remove_bg'):
                    payload['backgroundUrl'] = ""
                elif request.FILES.has_key('bg_image'):
                    file_request = FileMetadata.from_create_form(request.FILES['bg_image'])
                    try:
                        metadata = file_request.create((request.POST['site_subdomain_key'] + '.microco.sm'),
                            request.access_token)
                    except APIException as exc:
                        return respond_with_error(request, exc)
                    background_url = 'https://' + request.POST[
                        'site_subdomain_key'] + '.microco.sm/api/v1/files/' + metadata.file_hash
                    payload['backgroundUrl'] = background_url

            try:
                Site.update(request.META['HTTP_HOST'], site_id, payload, request.access_token)
            except APIException as exc:
                return respond_with_error(request, exc)
            return HttpResponseRedirect(reverse('dashboard-sites'))

        if request.GET:
            template_form_details = 'forms/site-edit-details.html'
            template_form_theme = 'forms/site-edit-theme.html'
            template_form_permissions = 'forms/site-edit-permissions.html'
            template_form_notifications = 'forms/site-edit-notifications.html'

            sections_templates = {
                'details': template_form_details,
                'theme': template_form_theme,
                'permissions': template_form_permissions,
                'notifications': template_form_notifications
            }

            site_url, params, headers = Site.build_request(request.META['HTTP_HOST'], site_id,
                access_token=request.access_token)
            request.view_requests.append(grequests.get(site_url, params=params, headers=headers))
            try:
                responses = response_list_to_dict(grequests.map(request.view_requests))
            except APIException as exc:
                respond_with_error(request, exc)
            site_for_edit = Site.from_summary(responses[site_url])
            context = {
                'user': Profile(responses[request.whoami_url], summary=False) if request.whoami_url else None,
                'site': request.site,
                'site_edit': site_for_edit,
                'default_logo': default_logo
            }

            if request.GET.get('section_name'):
                section_name = request.GET['section_name']
                if section_name in ['details', 'theme', 'permissions', 'notifications']:
                    context['section_name'] = section_name
                    context['edit_form'] = render(request, sections_templates[section_name],
                                                  {'site_edit': site_for_edit}).content
                else:
                    return HttpResponseNotFound()

            return render(request, SitesView.template_edit, context)
