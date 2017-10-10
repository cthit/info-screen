import feedparser
from inflection import parameterize
from mako.template import Template

def parse_alt_xkcd(entry):
	parsed_description = feedparser.parse(entry['description'])
	return parsed_description['feed']['img']['title']

parse_description = lambda entry: entry['description']

feeds = [{
	'name': "xkcd",
	'layout': "layout",
	'url': "https://xkcd.com/rss.xml",
	'count': 1,
	'parse_alt': parse_alt_xkcd
}, {
	'name': "chalmers-it",
	'layout': "chalmers-it",
	'url': "https://chalmers.it/posts.rss",
	'count': 3
}]

for feed_data in feeds:
	feed = feedparser.parse(feed_data.get('url'))
	items = []
	filename = parameterize(feed_data.get('name')) + ".html"
	f = open(filename, 'w')

	for i in range(0, feed_data.get('count')):
		entry = feed['entries'][i]
		item = {
			'title': entry['title'],
			'description': feed_data.get('parse_description', parse_description)(entry),
			'alt_text': feed_data.get('parse_alt', lambda x: '')(entry)
		}

		items.append(item)

	template = Template(filename="templates/%s.html" % (feed_data.get('layout')))
	f.write(template.render(items=items))
	f.close()