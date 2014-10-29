from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

from core.views import ErrorView

urlpatterns = patterns('',
	url(r'', include('updates.urls')),
	url(r'', include('core.urls')),
	url(r'', include('microcosm_site.urls')),
	url(r'', include('microcosm_admin.urls')),
)

handler403 = ErrorView.forbidden
handler404 = ErrorView.not_found
handler500 = ErrorView.server_error
