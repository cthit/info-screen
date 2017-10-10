import feedparser
from inflection import parameterize
from mako.template import Template
from datetime import datetime
import requests
import json

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

def out_filename(name):
	return "%s.html" % (name)

def template_path(template):
	return "templates/%s.html" % (template)

def fetch_feeds():
	for feed_data in feeds:
		feed = feedparser.parse(feed_data.get('url'))
		items = []
		filename = out_filename(parameterize(feed_data.get('name')))
		f = open(filename, 'w')

		for i in range(0, feed_data.get('count')):
			entry = feed['entries'][i]
			item = {
				'title': entry['title'],
				'description': feed_data.get('parse_description', parse_description)(entry),
				'alt_text': feed_data.get('parse_alt', lambda x: '')(entry)
			}

			items.append(item)

		template = Template(filename=template_path(feed_data.get('layout')))
		f.write(template.render(items=items))
		f.close()


def fetch_lunch():
	lunch_url = "https://lunch.chalmers.it/"

	r = requests.get(lunch_url)
	r.raise_for_status()


	f = open(out_filename("lunch"), 'w')
	template = Template(filename=template_path("lunch"))
	restaurants = json.loads(r.text)
	f.write(template.render(restaurants=[rest for rest in restaurants if rest['location'] != 'Lindholmen']))
	f.close()


def parse_date(date):
	date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
	return date.strftime("%H:%M")

def fetch_bookit():
	bookit_url = "https://bookit.chalmers.it/bookings/today.json"
	r = requests.get(bookit_url)
	r.raise_for_status()

	f = open(out_filename("bookit"), 'w')
	template = Template(filename=template_path("bookit"))
	bookings = json.loads(r.text)

	bookings = sorted(bookings, key=lambda booking: booking['begin_date'])

	for booking in bookings:
		booking['begin_date'] = parse_date(booking['begin_date'])
		booking['end_date'] = parse_date(booking['end_date'])

	bookings_by_room = {}

	for booking in bookings:
		bookings_by_room.setdefault(booking['room'], []).append(booking)

	f.write(template.render(bookings_by_room=bookings_by_room))
	f.close()

fetch_bookit()