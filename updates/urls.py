from django.conf.urls import patterns, url

from views import LandingView
from views import UpdateView

urlpatterns = patterns('',
	url(r'^updates/$', LandingView.landing),
	url(r'^updates/december/$', UpdateView.december),
)
