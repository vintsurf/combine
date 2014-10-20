import ConfigParser
import grequests
import json
import sys
from logger import get_logger
import logging


logger = get_logger('reaper')

def exception_handler(request, exception):
    logger.error("Request %r failed: %r" % (request, exception))

def get_feeds(feed_dictonary):
    # Inbound file://
    file_feeds={}
    for label, url in feed_dictonary.iteritems():
        if url.startswith('file://'):
            file_feeds[label] = url.partition('://')[2]
            feed_dictonary.remove(url)

    # Fire requests
    headers = {'User-Agent': 'harvest.py'}
    reqs = [grequests.get(url, headers=headers) for label, url in feed_dictonary.iteritems()]
    responses = grequests.map(reqs, exception_handler=exception_handler)
    
    # Now to build the response array, since there is no way yet to label a 
    # request with grequest, we must search the associated tag by looping the
    # inbound feed dict
    feed_harvest = []
    for response in responses:
        if response:
            for label, url in feed_dictonary.iteritems():
                if url == response.url:
                    feed_harvest.append((label, response.status_code, response.text))
    
    for label, each in file_feeds:
        with open(each,'rb') as f:
            feed_harvest.append((label, 200, f.read()))

    return feed_harvest

def reap(file_name):
    config = ConfigParser.SafeConfigParser(allow_no_value=False)
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        logger.error('Reaper: Could not read combine.cfg.')
        logger.error('HINT: edit combine-example.cfg and save as combine.cfg.')
        return

    inbound_urls = dict(config.items('feeds.inbound'))
    outbound_urls = dict(config.items('feeds.outbound'))

    logger.info('Fetching inbound URLs')
    inbound_files=[]
    for url in inbound_urls:
        if url.startswith('file://'):
            inbound_files.append(url.partition('://')[2])
            inbound_urls.remove(url)
    headers = {'User-Agent': 'harvest.py'}
    reqs = [grequests.get(url, headers=headers) for url in inbound_urls]
    inbound_responses = grequests.map(reqs, exception_handler=exception_handler)
    inbound_harvest = [(response.url, response.status_code, response.text) for response in inbound_responses if response]
    for each in inbound_files:
        try:
            with open(each,'rb') as f:
                inbound_harvest.append(('file://'+each, 200, f.read()))
        except IOError as e:
            assert isinstance(logger, logging.Logger)
            logger.error('Reaper: Error while opening "%s" - %s' % (each, e.strerror))

    logger.info('Fetching outbound URLs')
    outbound_files=[]
    for url in outbound_urls:
        if url.startswith('file://'):
            outbound_files.append(url.partition('://')[2])
            outbound_urls.remove(url)
    reqs = [grequests.get(url, headers=headers) for url in outbound_urls]
    outbound_responses = grequests.map(reqs, exception_handler=exception_handler)
    outbound_harvest = [(response.url, response.status_code, response.text) for response in outbound_responses if response]
    for each in outbound_files:
        try:
            with open(each,'rb') as f:
                outbound_harvest.append(('file://'+each, 200, f.read()))
        except IOError as e:
            assert isinstance(logger, logging.Logger)
            logger.error('Reaper: Error while opening "%s" - %s' % (each, e.strerror))

    logger.error('Storing raw feeds in %s' % file_name)
    harvest = {'inbound': inbound_harvest, 'outbound': outbound_harvest}

    with open(file_name, 'wb') as f:
        json.dump(harvest, f, indent=2)


if __name__ == "__main__":
    reap('harvest.json')
