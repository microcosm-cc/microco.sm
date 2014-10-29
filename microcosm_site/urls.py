from django.conf.urls import url
from django.conf.urls import patterns

from microcosm_site.views import AboutView
from microcosm_site.views import FaqsView
from microcosm_site.views import CompareView
from microcosm_site.views import DevelopersView
from microcosm_site.views import LegalView
from microcosm_site.views import FeaturesView
from microcosm_site.views import LandingView


urlpatterns = patterns('',
	url(r'^$', LandingView.index, name='site-home'), # Launched
	#url(r'^home/$', LandingView.index, name='site-home'), # Unlaunched
	url(r'^about/$', AboutView.index, name='site-about'),
	url(r'^faqs/$', FaqsView.index, name='site-faqs'),
	url(r'^compare/$', CompareView.index, name='site-compare'),
	url(r'^developers/$', DevelopersView.index, name='site-developers'),
	url(r'^features/$', FeaturesView.index,  name='site-features'),

	url(r'^terms/$', LegalView.terms, name='site-terms'),
	# url(r'^status/', LegalView.index, name='status'),
)
