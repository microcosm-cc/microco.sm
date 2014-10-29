def build_pagination_links(request, paged_list):
	"""
	This takes the data sent in the 'links' part of an api response
	and generates a dictionary of navigation links based on that.
	"""

	page_nav = {}

	for item in request:
		page_nav[item['rel']] = str.replace(str(item['href']),'/api/v1','')

	return page_nav
