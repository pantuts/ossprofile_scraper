#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# by: pantuts
# http://pantuts.com
# Dependencies: python2.7, BeautifulSoup4, gevent
# Licence? None. Do what you want. Just a credit is fine.
# Agreement: This script is for educational purposes only. By using this script you agree
# that you alone will be responsible for any act you make. The author will not be liable
# of your actions.

import gevent.monkey
gevent.monkey.patch_all()

from bs4 import BeautifulSoup
from urllib2 import urlopen, Request, build_opener, URLError
import csv
import sys


def usage():
    print('python ossprofile_scraper.py links.txt')


def scrape(num, url):
    soup = requestor(num, url)
    # if all is well
    if soup:
        name = get_name(soup)
        avatar = get_avatar(soup)
        role, company, company_location = get_rcl(soup)
        social_sites, website = get_sites(soup)
        description = get_desc(soup)
        friends = get_friends(soup)

        # output
        data = [
            url,
            name.encode('utf-8'),
            avatar,
            role.encode('utf-8'),
            company.encode('utf-8'),
            company_location.encode('utf-8'),
            [social_sites],
            website,
            description.encode('utf-8'),
            friends
        ]
        write_row(data, 'OpenStackSummitProfiles.csv')

        print '[+] Done - ' + str(num)


def requestor(num, url):
    try:
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.146 Safari/537.36')
        opener = build_opener()
        print '[+] ' + str(num), 'Scraping: ' + url
        res = opener.open(req)
        response = res.read()
        soup = BeautifulSoup(response, 'html.parser')
        return soup
    except URLError, e:
        print '[-][' + str(num) + '] ' + str(e)
        # write not found url
        with open("NOT FOUND URLs.txt", "a+") as f:
            f.write('Row: ' + str(num) + ' - ' + url + '\n')
        pass
    except Exception, e:
        print '[-][' + str(num) + '] ' + str(e)
        pass


def get_avatar(soup):
    if soup.select('#myavatar'):
        avatar = [i.get('src') for i in soup.select('#myavatar')][0]
        return avatar.replace('https://', '').replace('http://', '').replace('//', '')
    else: return ''


def get_name(soup):
    if soup.select('#sched-page-me-name'):
        return ''.join(soup.select('#sched-page-me-name')[0]).strip()
    else: return ''


def get_rcl(soup):
    loc = ''
    company = ''
    role = ''
    if soup.select('#sched-page-me-profile-data'):
        for i in soup.select('#sched-page-me-profile-data'):
            # commented is the previous content structure
            # if i.next:
            #     tmp_rcl = i.next.strip().split(',')
            #     role = tmp_rcl[0]
            #     if len(tmp_rcl) > 2:
            #         role = tmp_rcl[0] + ', ' + tmp_rcl[1]
            #         company = tmp_rcl[-1]
            #     if len(tmp_rcl) == 2:
            #         role = tmp_rcl[0]
            #         company = tmp_rcl[1]
            # if i.br:
            #     loc = i.br.next_sibling.strip()
            company = i.strong.text.strip() if i.strong else ''
            if (i.br.next.name not in ['div', None]) or (i.next and i.next.name not in ['div', 'br']):
                role = i.br.next_sibling.strip() or i.next.strip()
            else: role = ''
            if i.br.next.next.next.name != 'div' and i.br.next.next.next_sibling is not None:
                loc = i.br.next.next.next_sibling.strip()
            else: loc = ''
        r, c, l = role.strip(), company.strip(), loc.strip()
    else: r, c, l = '', '', ''

    return r, c, l


def get_sites(soup):
    social = []
    website = ''
    if soup.select('div.sched-network-link a'):
        for i in soup.select('div.sched-network-link a'):
            if i.select('img[alt="Website"]'):
                website = i.get('href')
            else:
                social.append(str(i.get('href')))
            s, w = ', '.join(social), website
    else: s, w = '', ''

    return s, w


def get_desc(soup):
    if soup.select('#sched-page-me-profile-about'):
        return ''.join([i.get_text() for i in soup.select('#sched-page-me-profile-about')][0]).strip()
    else: return ''


def get_friends(soup):
    if soup.select('#sched-page-me-connections ul li a'):
        return ['http://openstacksummitmay2014atlanta.sched.org' + str(i.get('href')) for i in soup.select('#sched-page-me-connections ul li a')]
    else: return ''


def create_csv(fname):
    with open(fname, 'a+') as f:
        writer = csv.writer(f)
        writer.writerow(('URL', 'Name', 'Avatar', 'Role', 'Company', 'Location', 'Social Sites', 'Website', 'Description', 'Friends'))


def write_row(data, fname):
    with open(fname, 'a+') as f:
        writer = csv.writer(f)
        writer.writerow(data)


if __name__=='__main__':
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    create_csv('OpenStackSummitProfiles.csv')

    with open(sys.argv[1], 'r') as f:
        urls = [url.strip() for url in f.readlines()]

    threads = []
    for i in range(len(urls)):
        threads.append(gevent.spawn(scrape, i + 1, urls[i]))
        if (i + 1) % 20 == 0:
            gevent.joinall(threads)
        else:
            continue
    gevent.joinall(threads)

    print('By: Pantuts')




