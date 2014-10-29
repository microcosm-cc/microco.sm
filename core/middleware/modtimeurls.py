# http://ole-laursen.blogspot.co.uk/2010/11/cache-busting-in-django.html
# http://people.iola.dk/olau/python/
# http://people.iola.dk/olau/python/modtimeurls.py
#
# Simple middleware to search and replacing src="" and href="" in HTML
# responses to add ?_=<modification time> on links to files that
# reside in MEDIA_ROOT or STATIC_ROOT:
#
#  <img src="/media/foo.jpg"> -> <img src="/media/foo.jpg?_=432101234">
#
# The neat thing is that static file servers ignore the GET parameters
# when they are serving files, thus the modified URL still points to
# the same file but will change as soon as the file changes,
# alleviating problems with the markup and scripts/images/CSS getting
# out of sync.
#
# Dump this file in your project and enable it with something like
# this in your settings.py:
#
# MIDDLEWARE_CLASSES = (
#    ...
#    'modtimeurls.ModTimeUrlsMiddleware',
#    )
#
# As a bonus, with the middleware enabled in Django, one can instruct
# whatever is serving the static files to add a cache expiration far
# out in the future on files served with a _ GET parameter to enable
# all upstream caches including the browser to make as much use of the
# files as possible.
#
# For instance, for lighttpd, something like this can be used:
#
#   $HTTP["querystring"] =~ "^_=" { expire.url = ( "" => "access 1 years") }
#
# For nginx, something like this:
#
#   location /media/ {
#     if ($args ~ "^_=") { expires 1y; }
#   }
#
# By Ole Laursen, sponsored by IOLA, November 2010.
# - changed July 27, 2012 to add support for STATIC_ROOT

import re, os
import pylibmc as memcache

from django.conf import settings

url_attributes = ['src', 'href']

# stop matching when we hit <, > or " to guard against erratic markup
link_matcher = re.compile(u'((?:%s)="(?:%s|%s)[^<>"]*")' % ("|".join(url_attributes), re.escape(settings.STATIC_URL), re.escape(settings.MEDIA_URL)))

class ModTimeUrlsMiddleware:
    """Middleware for adding modtime GET parameter to each media URL in responses."""

    def __init__(self):
        # cache of hit file last modified times
        self.mc = memcache.Client(['%s:%d' % (settings.MEMCACHE_HOST, settings.MEMCACHE_PORT)])

    def append_modtime_to_url(self, url):
        """Append the file modification time to URL if the URL is in
        STATIC_URL/MEDIA_URL and corresponds to a file in
        STATIC_ROOT/MEDIA_ROOT. This function can be used standalone in
        case there are links not catched by the middleware."""
        static = url.startswith(settings.STATIC_URL)
        media = url.startswith(settings.MEDIA_URL)
        if not (static or media):
            return url

        if url == '/':
            return url

        if static:
            filename = os.path.join(settings.STATIC_ROOT, url[len(settings.STATIC_URL):])
        else:
            filename = os.path.join(settings.MEDIA_ROOT, url[len(settings.MEDIA_URL):])

        index = filename.rfind('?')
        contains_question_mark = index != -1
        
        if contains_question_mark:
            if filename[index:].find("_=") != -1: # url already has a _=, skip it
                return url

            filename = filename[:index]

        try:
            mc_ts = self.mc.get('fmod_' + filename)
        except memcache.Error:
            mc_ts = None

        try:
            if not mc_ts is None:
                return url + ('&' if contains_question_mark else '?') + "_=" + mc_ts

            stat = os.stat(filename)
            timestamp = str(int(stat.st_mtime))

            try:
                self.mc.set('fmod_' + filename, timestamp)
            except memcache.Error as e:
                pass

            return url + ('&' if contains_question_mark else '?') + "_=" + timestamp
        except OSError:
            pass

        return url

    def process_response(self, request, response):
        """Add modification time GET parameter to each media URL in input."""
        def replace_urls(m):
            before, url, after = m.group(1).split('"')

            return before + '"' + self.append_modtime_to_url(url) + '"' + after

        if 'text/html' in response['content-type'].lower():
            response.content = link_matcher.sub(replace_urls, response.content)

        return response