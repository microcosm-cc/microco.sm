from django.conf.urls import url
from django.conf.urls import patterns

from microcosm_admin.views import SitesView


urlpatterns = patterns('',
	url(r'^dashboard/$', SitesView.list, name='dashboard'),
	url(r'^dashboard/sites/$', SitesView.list, name='dashboard-sites'),
	url(r'^dashboard/sites/create/$', SitesView.create, name='dashboard-sites-create'),
	url(r'^dashboard/sites/edit/(?P<site_id>\d+)/$', SitesView.edit, name='dashboard-sites-edit'),
)
