import feedparser
from inflection import parameterize
from mako.template import Template
from datetime import datetime
import requests, json


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
	return f"{name}.html"


def template_path(template):
	return f"templates/{template}.html"


def fetch_feeds():
	for feed_data in feeds:
		feed = feedparser.parse(feed_data.get('url'))
		items = []
		filename = out_filename(parameterize(feed_data.get('name')))

		for i in range(0, feed_data.get('count')):
			entry = feed['entries'][i]
			item = {
				'title':
				entry['title'],
				'description':
				feed_data.get(
					'parse_description',
					parse_description
				)(entry),
				'alt_text':
				feed_data.get('parse_alt', lambda x: '')(entry)
			}

			items.append(item)

		template = Template(
			filename=template_path(feed_data.get('layout')))

		with open(filename, 'w') as f:
			f.write(template.render(items=items))


def fetch_lunch():
	lunch_url = "https://lunch.chalmers.it/"

	r = requests.get(lunch_url)
	r.raise_for_status()

	template = Template(filename=template_path("lunch"))
	restaurants = json.loads(r.text)

	with open(out_filename("lunch"), 'w') as f:
		f.write(template.render(
			restaurants=[
				rest for rest in restaurants
				if rest['location'] != 'Lindholmen']))


def parse_date(date, fmt="%H:%M"):
	date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
	return date.strftime(fmt)


def fetch_bookit():
	bookit_url = "https://bookit.chalmers.it/bookings/today.json"
	r = requests.get(bookit_url)
	r.raise_for_status()
	
	template = Template(filename=template_path("bookit"))
	bookings = json.loads(r.text)

	bookings = sorted(bookings, key=lambda booking: booking['begin_date'])

	for booking in bookings:
		booking['day'] = parse_date(booking['begin_date'], "%Y-%m-%d")
		booking['begin_date'] = parse_date(booking['begin_date'])
		booking['end_date'] = parse_date(booking['end_date'])

	bookings_by_room = {}

	for booking in bookings:
		bookings_by_room.setdefault(booking['room'], {})\
						.setdefault(booking['day'], [])\
						.append(booking)

	with open(out_filename("bookit"), 'w') as f:
		f.write(template.render(bookings_by_room=bookings_by_room))


fetch_bookit()
fetch_lunch()
fetch_feeds()
