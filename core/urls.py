from django.conf.urls import url
from django.conf.urls import patterns

from core.views import FaviconView
from core.views import RobotsView
from core.views import ProfileView
from core.views import AuthenticationView
from core.views import Auth0View


urlpatterns = patterns('',
	url(r'^robots\.txt$', RobotsView.as_view()),
	url(r'^favicon\.ico$', FaviconView.as_view()),

	# Echoes request headers
	url(r'^headers/', 'core.views.echo_headers'),

	# Auth
	url(r'^login/$', AuthenticationView.login, name='login'),
    url(r'^auth0login/$', Auth0View.login, name='auth0login'),
	url(r'^logout/$', AuthenticationView.logout, name='logout'),

	# User profiles
	url(r'^profiles/(?P<profile_id>\d+)/$', ProfileView.single, name='single-profile'),
)
