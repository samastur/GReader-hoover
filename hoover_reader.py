#!/usr/bin/env python

import os
from os.path import join
import sys
import json
import time
from libgreader import GoogleReader, ClientAuthMethod, Category

try:
    import settings
except ImportError:
    settings = object()

import re
import unidecode

def slugify(str):
    str = unidecode.unidecode(str).lower()
    return re.sub(r'\W+','-',str)

BACKUP_DIR = getattr(settings, 'BACKUP_DIRECTORY', 'reader_backup')
PAUSE_INTERVAL = 60


def toJSON(obj):
    return json.dumps(obj, sort_keys=True, indent=2)


class HooverReader(object):
    '''
    Export everything that was saved in Google Reader as JSON objects. Keep
    as much information as possible, but especially ID (useful for
    cross-referencing), title, url, notes (probably gone) and read status.
    Each file should contain entries for just one category/tag. List of
    categories (folders in Google Reader) should be stores in categories.json.

    Script has no memory and will always fetch everything (doesn't do
    incremental updates). Script will NOT save list of feeds since those can
    be exported as OPML from Google Reader.

    If it hits rate limit, then it will pause up to half an hour before giving
    up.

    DILEMMAS:
    - Should we save feeds contents? How far?
    - Should we save categories contents? How far?
        (probably; categories can contain entries labeled with category label
         that are not otherwise tagged and hence not backed up)

    Save:
    - all tagged entries (labeled feeds; categories that don't contain feeds)
    - list of categories with feeds they contain

    Algorithm:
    - fetch a list of categories
    - fetch a list of all labels (which includes categories)
    - for every label which is not a category:
        - loadItems
        - execute loadMoreItems until items count remains same (or error)
        - dump data as JSON to file
    - for every category fetch a list of feeds it contains
    - dump the list of categories with feeds as JSON to a file
    '''
    def __init__(self, username, password):
        self.auth = ClientAuthMethod(username, password)
        self.reader = GoogleReader(self.auth)
        self.reader.makeSpecialFeeds()  # Fetches list of special feeds like starred
        self.reader.buildSubscriptionList()  # Fetches list of feeds AND categories

        self.categories = self.reader.categories
        self.feeds = self.reader.feeds[:]  # Make a copy so lib calls don't feel it with crap
        self.specialFeeds = self.reader.specialFeeds.copy()

    def __create_feed_filename(self, feed_label):
        return "{0}.json".format(slugify(feed_label))

    def get_tags(self):
        tags_json = self.reader.httpGet(
            'https://www.google.com/reader/api/0/tag/list',
            {'output': 'json'})
        tags = json.loads(tags_json)
        tags_list = tags['tags']
        self.tags = tags_list

    def load_items(self, feed):
        fetch_size = 1000
        tryagain = 0
        feed.loadItems(loadLimit=fetch_size)
        while (feed.lastLoadLength > 0 and feed.lastLoadLength == fetch_size) \
                or (tryagain > 0 and tryagain < 5):
            feed.loadMoreItems(loadLimit=fetch_size)
            if not feed.lastLoadOk:
                print "Error fetching items for feed '{0}'".format(
                    feed.title)
                pause_for = PAUSE_INTERVAL * (2 ** tryagain)
                print "Pausing for a {0} minute(s)...".format(pause_for / 60)
                # Double time to sleep on each iteration
                time.sleep(pause_for)
                tryagain += 1
            else:
                tryagain = 0
        return feed.items

    def process_item(self, item):
        values = {}
        keys = ('id', 'title', 'content', 'read', 'starred', 'shared', 'url')
        for key in keys:
            values[key] = getattr(item, key, u'')
        values['origin'] = getattr(item, 'origin', {})
        return values

    def get_feed_info(self, feed):
        feed_obj = {
            'feed_id': feed.id,
            'title': feed.title,
            'site_url': getattr(feed, "siteUrl", ""),
            'feed_url': getattr(feed, "feedUrl", ""),
            'last_updated': feed.lastUpdated,  # Unix timestamp; updated when feed is fetched
        }
        return feed_obj

    def save_to_file(self, filename, obj, subdir=None):
        save_dir = BACKUP_DIR
        if subdir:
            save_dir = join(BACKUP_DIR, subdir)
        if not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir)
            except:  # Could not create it
                print 'Could not create backup directory {0}. Exiting.'.format(
                    save_dir)
                sys.exit(1)

        obj_json = toJSON(obj)
        fname = join(save_dir, filename)
        with open(fname, 'w') as f:
            f.write(obj_json)

    def save_feed(self, feed, subdir=None):
        items = []

        print 'Saving:', feed.title.encode('utf-8')
        try:
            raw_items = self.load_items(feed)
        except:
            print 'Failed. Moving on...'
            print
            return
        for item in raw_items:
            items.append(self.process_item(item))
        feed_obj = self.get_feed_info(feed)
        feed_obj['items'] = items
        feed_obj['items_count'] = len(items)
        self.save_to_file(self.__create_feed_filename(unicode(feed.title)), feed_obj, subdir)

    def process_category(self, category):
        cat = {
            'id': category.id,
            'title': category.label,
        }
        cat['feeds'] = [self.get_feed_info(feed) for feed in category.feeds]
        return cat

    def save_tag(self, tag):
        cat = {
            'id': tag.id,
            'title': tag.label,
        }
        print 'Saving:', tag.label.encode('utf-8')
        cat['items'] = [self.process_item(item) for item in
                        self.load_items(tag)]
        cat['items_count'] = len(cat['items'])
        self.save_to_file(self.__create_feed_filename(unicode(cat['title'])), cat, 'tags')

    def save_categories(self):
        categories = {
            'title': 'Google Reader Categories'
        }
        categories['categories'] = [self.process_category(cat) for cat in
                                    self.categories]
        if len(categories['categories']):
            self.save_to_file("categories.json", categories)
        else:
            print 'There are no categories to save.'

    def save_feed_list(self):
        feeds = {
            'title': 'Google Reader List of Feeds'
        }
        feeds_list = []
        for feed in self.feeds:
            feeds_list.append(self.get_feed_info(feed))
        feeds['feeds'] = feeds_list
        if len(feeds['feeds']):
            self.save_to_file("feeds.json", feeds)
        else:
            print 'There are no feeds to save.'

    def backup(self):
        if getattr(settings, 'SAVE_TAGS', True):
            print "Saving tags..."
            self.get_tags()
            for tag in self.tags:
                # Tag is really a category
                try:
                    label = tag['id'].rsplit('label/')[1]
                except:
                    # Special feeds (state/); skip, they are handled separately
                    continue
                ctag = Category(self.reader, label, tag['id'])
                self.save_tag(ctag)

        if getattr(settings, 'SAVE_FEEDS', False):
            print "Saving feeds..."
            for feed in self.feeds:
                self.save_feed(feed, 'feeds')

        print "Saving special feeds..."
        if getattr(settings, 'SAVE_SPECIAL_FEEDS_ALL', False):
            sf_keys = self.specialFeeds.keys()
        else:
            sf_keys = ('starred', )
        for feed_name in sf_keys:
            feed = self.specialFeeds[feed_name]
            self.save_feed(feed, 'special')

        if getattr(settings, 'SAVE_CATEGORIES', True):
            print "Saving list of feeds and categories..."
            self.save_feed_list()
            self.save_categories()


if __name__ == '__main__':
    if len(sys.argv) == 3:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        username = getattr(settings, 'USERNAME')
        password = getattr(settings, 'PASSWORD')
    if username and password:
        hoover = HooverReader(username, password)
        hoover.backup()
    else:
        print 'Username and password missing. Add them to settings.py or provide them as arguments to the script.'
