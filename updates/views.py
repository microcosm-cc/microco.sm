from django.http import HttpResponse
from django.template import RequestContext
from django.template import loader
from django.views.generic.base import TemplateView


class LandingView(TemplateView):

	@staticmethod
	def landing(request):
		context = RequestContext(request, {})
		return HttpResponse(loader.get_template('landing.html').render(context))


class UpdateView(TemplateView):

	@staticmethod
	def december(request):
		context = RequestContext(request, {})
		return HttpResponse(loader.get_template('archives/december.html').render(context))