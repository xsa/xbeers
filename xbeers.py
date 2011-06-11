#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2011 Xavier Santolaria <xavier@santolaria.net>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import codecs
import datetime
import getpass
import sys
import untappd

from optparse import OptionParser

sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

MY_UNTAPPD_API_KEY = ""

UNTAPPD_PROTO = 'http://'
UNTAPPD_URL = 'untappd.com'
UNTAPPD_API_BASE_URL = 'api.untappd.com'
UNTAPPD_API_VERSION="v3"
UNTAPPD_DFLT_OFFSET = 25

UNTAPPD_BASE_BEER_URL = UNTAPPD_PROTO + UNTAPPD_URL + '/beer'


TWITTER_BASE_URL = "https://twitter.com"

now = datetime.datetime.utcnow()


def main():
    parser = OptionParser(usage="usage: %prog [options]", version="%prog 0.1")
    parser.add_option("-a", "--auth",
                      action="store_true",
                      dest="auth",
                      help="use authenticated mechanism")
    parser.add_option("-u", "--user",
                      action="store",
                      dest="username",
                      help="specify username to query data from")
    (options, args) = parser.parse_args()

    if options.username is None:   # Username is required
        parser.error('Username not given')

    user = options.username
    passwd = None

    if options.auth is not None:
        passwd = getpass.getpass()
        if not passwd:
            sys.exit("Error: no password entered.")

    c = count = 0

    u = untappd.Api(MY_UNTAPPD_API_KEY, user, passwd)

    l = get_user_beers(u, user)
    slist = sortDictBy(l, 'country')	# Sort first by country

    count = len(slist)

    print_html_header(count)

    # Build the countries list at the top
    print_html_countries_list(slist)

    i = 0
    for sub in slist:
        if sub['country'] != c:
            if i > 0:
                print '</ol>'
                print ''
            print_html_country_header(sub['country'])
       
        print_html_beer_item(sub['beer_id'], sub['beer'], sub['twitter'])

        c = sub['country']
        i = i + 1

    print_html_footer()

########## Functions ##########

def sortDictBy(list, key):
    nlist = map(lambda x, key=key: (x[key], x), list)
    nlist.sort()
    return map(lambda (key, x): x, nlist)


def get_user_beers(u, user):
    offset = 0
    bdata = []

    while True:
        data = u.get_user_distinct(**{'user': user, 'offset': offset})

        for result in data['results']:
            if result.get('brewery_id'):
                brdata = get_brewery_info(u, result['brewery_id'])

                this_beer = {
                    'beer':result.get('beer_name'),
                    'beer_id':result.get('beer_id'),
                    'twitter':brdata[1] or None
                }
                this_beer['country'] = brdata[0]

                bdata.append(this_beer)

        if data.get('next_page'):
            offset = offset + UNTAPPD_DFLT_OFFSET
        else:
            break 

    return bdata


def get_brewery_info(u, id):
    l = []

    data = u.get_brewery_info(id)

    l.append(data['results']['country'])
    l.append(data['results']['twitter_handle'])

    return l


def print_html_beer_item(beer_id, beer, twitter_handle):
    print "<li><a href=\"%s%c%s\" target=\"_blank\">%s</a></li>" \
        % (UNTAPPD_BASE_BEER_URL, '/', beer_id, beer)


def print_html_countries_list(l):
    c = None

    print ''
    print '<table border="0" cellspacing="0" cellpadding="2" width="95%">'
    print '<tr>'
    print '<td valign="top" width="20%">'
    print '<ul>'


    i = 0
    for sub in l:
         if sub['country'] != c:
             print ('<li><a href="#' + sub['country'] + '">' + sub['country'] +
                 '</a></li>')

         c = sub['country']
         i = i + 1

    print '</ul>'
    print '</td>'
    print '</tr>'
    print '</table>'
    print ''


def print_html_country_header(country):
    tld = None

    # Sorted by TLD
    countries = {
        'Ascension Island' : 'ac',
        'Andorra' : 'ad',
        'United Arab Emirates' : 'ae',
        'Afghanistan' :  'af',
        'Antigua and Barbuda' :  'ag',
        'Anguilla' :     'ai',
        'Albania' :      'al',
        'Armenia' :      'am',
        'Netherlands Antilles' :         'an',
        'Angola' :       'ao',
        'Antarctica' :   'aq',
        'Argentina' :    'ar',
        'American Samoa' :       'as',
        'Austria' :      'at',
        'Australia' :    'au',
        'Aruba' :        'aw',
        'Åland' :        'ax',
        'Azerbaijan' :   'az',
        'Bosnia and Herzegovina' :       'ba',
        'Barbados' :     'bb',
        'Bangladesh' :   'bd',
        'Belgium' :      'be',
        'Burkina' :      'bf',
        'Bulgaria' :     'bg',
        'Bahrain' :      'bh',
        'Burundi' :      'bi',
        'Benin' :        'bj',
        'Bermuda' :      'bm',
        'Brunei Darussalam' :    'bn',
        'Bolivia' :      'bo',
        'Brazil' :       'br',
        'Bahamas' :      'bs',
        'Bhutan' :       'bt',
        'Bouvet Island' :        'bv',
        'Botswana' :     'bw',
        'Belarus' :      'by',
        'Belize' :       'bz',
        'Canada' :       'ca',
        'Cocos (Keeling) Islands' :      'cc',
        'Democratic Republic of the Congo' :     'cd',
        'Central African Republic' :     'cf',
        'Republic of the Congo' :        'cg',
        'Switzerland' :  'ch',
        'Côte d\'Ivoire' :       'ci',
        'Cook Islands' :         'ck',
        'Chile' :        'cl',
        'Cameroon' :     'cm',
        'People\'s Republic of China' :  'cn',
        'Colombia' :     'co',
        'Costa Rica' :   'cr',
        'Cuba' :         'cu',
        'Cape Verde' :   'cv',
        'Christmas Island' :     'cx',
        'Cyprus' :       'cy',
        'Czech Republic' :       'cz',
        'Germany' :      'de',
        'Djibouti' :     'dj',
        'Denmark' :      'dk',
        'Dominica' :     'dm',
        'Dominican Republic' :   'do',
        'Algeria' :      'dz',
        'Ecuador' :      'ec',
        'Estonia' :      'ee',
        'Egypt' :        'eg',
        'Eritrea' :      'er',
        'Spain' :        'es',
        'Ethiopia' :     'et',
        'Finland' :      'fi',
        'Fiji' :         'fj',
        'Falkland Islands' :     'fk',
        'Federated States of Micronesia' :       'fm',
        'Faroe Islands' :        'fo',
        'France' :       'fr',
        'Gabon' :        'ga',
        'Grenada' :      'gd',
        'Georgia' :      'ge',
        'French Guiana' :        'gf',
        'Guernsey' :     'gg',
        'Ghana' :        'gh',
        'Gibraltar' :    'gi',
        'Greenland' :    'gl',
        'The Gambia' :   'gm',
        'Guinea' :       'gn',
        'Guadeloupe' :   'gp',
        'Equatorial Guinea' :    'gq',
        'Greece' :       'gr',
        'South Georgia and the South Sandwich Islands' :         'gs',
        'Guatemala' :    'gt',
        'Guam' :         'gu',
        'Guinea-Bissau' :        'gw',
        'Guyana' :       'gy',
        'Hong Kong' :    'hk',
        'Heard Island and McDonald Islands' :    'hm',
        'Honduras' :     'hn',
        'Croatia' :      'hr',
        'Haiti' :        'ht',
        'Hungary' :      'hu',
        'Indonesia' :    'id',
        'Ireland' :      'ie',
        'Israel' :       'il',
        'Isle of Man' :  'im',
        'India' :        'in',
        'British Indian Ocean Territory' :       'io',
        'Iraq' :         'iq',
        'Iran' :         'ir',
        'Iceland' :      'is',
        'Italy' :        'it',
        'Jersey' :       'je',
        'Jamaica' :      'jm',
        'Jordan' :       'jo',
        'Japan' :        'jp',
        'Kenya' :        'ke',
        'Kyrgyzstan' :   'kg',
        'Cambodia' :     'kh',
        'Kiribati' :     'ki',
        'Comoros' :      'km',
        'Saint Kitts and Nevis' :        'kn',
        'Democratic People\'s Republic of Korea' :       'kp',
        'Republic of Korea' :    'kr',
        'Kuwait' :       'kw',
        'Cayman Islands' :       'ky',
        'Kazakhstan' :   'kz',
        'Laos' :         'la',
        'Lebanon' :      'lb',
        'Saint Lucia' :  'lc',
        'Liechtenstein' :        'li',
        'Sri Lanka' :    'lk',
        'Liberia' :      'lr',
        'Lesotho' :      'ls',
        'Lithuania' :    'lt',
        'Luxembourg' :   'lu',
        'Latvia' :       'lv',
        'Libya' :        'ly',
        'Morocco' :      'ma',
        'Monaco' :       'mc',
        'Moldova' :      'md',
        'Montenegro' :   'me',
        'Madagascar' :   'mg',
        'Marshall Islands' :     'mh',
        'Republic of Macedonia' :        'mk',
        'Mali' :         'ml',
        'Myanmar' :      'mm',
        'Mongolia' :     'mn',
        'Macau' :        'mo',
        'Northern Mariana Islands' :     'mp',
        'Martinique' :   'mq',
        'Mauritania' :   'mr',
        'Montserrat' :   'ms',
        'Malta' :        'mt',
        'Mauritius' :    'mu',
        'Maldives' :     'mv',
        'Malawi' :       'mw',
        'Mexico' :       'mx',
        'Malaysia' :     'my',
        'Mozambique' :   'mz',
        'Namibia' :      'na',
        'New Caledonia' :        'nc',
        'Niger' :        'ne',
        'Norfolk Island' :       'nf',
        'Nigeria' :      'ng',
        'Nicaragua' :    'ni',
        'Netherlands' :  'nl',
        'Norway' :       'no',
        'Nepal' :        'np',
        'Nauru' :        'nr',
        'Niue' :         'nu',
        'New Zealand' :  'nz',
        'Oman' :         'om',
        'Panama' :       'pa',
        'Peru' :         'pe',
        'French Polynesia' :     'pf',
        'Papua New Guinea' :     'pg',
        'Philippines' :  'ph',
        'Pakistan' :     'pk',
        'Poland' :       'pl',
        'Saint-Pierre and Miquelon' :    'pm',
        'Pitcairn Islands' :     'pn',
        'Puerto Rico' :  'pr',
        'Palestinian territories West Bank' :    'ps',
        'Portugal' :     'pt',
        'Palau' :        'pw',
        'Paraguay' :     'py',
        'Qatar' :        'qa',
        'Réunion' :      're',
        'Romania' :      'ro',
        'Serbia' :       'rs',
        'Russia' :       'ru',
        'Rwanda' :       'rw',
        'Saudi Arabia' :         'sa',
        'Solomon Islands' :      'sb',
        'Seychelles' :   'sc',
        'Sudan' :        'sd',
        'Sweden' :       'se',
        'Singapore' :    'sg',
        'Saint Helena' :         'sh',
        'Slovenia' :     'si',
        'Svalbard and Jan Mayen' :       'sj',
        'Slovakia' :     'sk',
        'Sierra Leone' :         'sl',
        'San Marino' :   'sm',
        'Senegal' :      'sn',
        'Somalia' :      'so',
        'Suriname' :     'sr',
        'São Tomé and Príncipe' :        'st',
        'Soviet Union' :         'su',
        'El Salvador' :  'sv',
        'Syria' :        'sy',
        'Swaziland' :    'sz',
        'Turks and Caicos Islands' :     'tc',
        'Chad' :         'td',
        'French Southern and Antarctic' :        'tf',
        'Togo' :         'tg',
        'Thailand' :     'th',
        'Tajikistan' :   'tj',
        'Tokelau' :      'tk',
        'East Timor' :   'tl',
        'Turkmenistan' :         'tm',
        'Tunisia' :      'tn',
        'Tonga' :        'to',
        'East Timor' :   'tp',
        'Turkey' :       'tr',
        'Trinidad and Tobago' :  'tt',
        'Tuvalu' :       'tv',
        'Republic of China (Taiwan)' :   'tw',
        'Tanzania' :     'tz',
        'Ukraine' :      'ua',
        'Uganda' :       'ug',
        'England' :      'uk',
        'United Kingdom' :       'uk',
        'United States' :     'us',
        'Uruguay' :      'uy',
        'Uzbekistan' :   'uz',
        'Vatican City' :         'va',
        'Saint Vincent and the Grenadines' :     'vc',
        'Venezuela' :    've',
        'British Virgin Islands' :       'vg',
        'U.S. Virgin Islands' :  'vi',
        'Vietnam' :      'vn',
        'Vanuatu' :      'vu',
        'Wallis and Futuna' :    'wf',
        'Samoa' :        'ws',
        'Yemen' :        'ye',
        'Mayotte' :      'yt',
        'South Africa' :         'za',
        'Zambia' :       'zm',
        'Zimbabwe' :     'Zw'
    }


    for k, v in countries.items():
        if isinstance(country, unicode):
            country = country.encode('utf-8') 
        if country == k:
            tld = v

    print '<a name="' + country + '"></a>'
    print '<div class="head-category">'
    print '<h2>'
    print '<img src="images/icons/flags/png/' + str(tld) +'.png" width="16" height="11" alt=".' + str(tld) + '" />'
    print country
    print '</h2>'
    print '</div>'
    print '<ol>'


def print_html_header(count):
    print '<?xml version="1.0" ?>'
    print '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"'
    print '  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
    print '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">'
    print '<head>'
    print '  <link rel="stylesheet" href="style.css" type="text/css" />'
    print '  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />'
    print '  <meta name="keywords" content="unix,openbsd,security,programming,hacking,beers" />'
    print '  <title>Beers I\'ve already drunk</title>'
    print '</head>'
    print '<body>'
    print ''
    print '<center>'
    print '<script type="text/javascript"><!--'
    print 'google_ad_client = "pub-3558105154926044";'
    print 'google_ad_slot = "5380311117";'
    print 'google_ad_width = 728;'
    print 'google_ad_height = 90;'
    print '//-->'
    print '</script>'
    print '<script type="text/javascript"'
    print 'src="http://pagead2.googlesyndication.com/pagead/show_ads.js">'
    print '</script>'
    print '</center>'
    print ''
    print '<h1 class="masthead">Beers I\'ve already drunk</h1>'
    print ''
    print '<p>'
    print 'Here is a list of the beers from all around the world I\'ve already drunk.'
    print 'This is of course a work in progress,'
    print '<a href="wishlist.html">donations</a> accepted ;-)'
    print '</p>'
    print ''
    print '<p>'
    print 'Last count as of ' + str(now.strftime("%Y/%m/%d %H:%M %z")) + ': <b>'+ str(count) + '</b> beers.'
    print '</p>'


def print_html_footer():
    print '</ol>'
    print ''
    print '<br />'
    print ''
    print '<table width="100%" border="0" cellspacing="0" cellpadding="0">'
    print '<tr class="footer">'
    print '  <td class="footer" valign="top">'
    print '    Copyright &copy; 2003-%d,' % now.year
    print '     <a href="mailto:xavier@santolaria.net">Xavier Santolaria</a>.'
    print '     All rights reserved.'
    print '  </td>'
    print '  <td class="footer" valign="middle" align="right">'
    print '    <a href="http://www.eff.org/br/"><img src="blueribbon.gif"'
    print '     alt="Join the Blue Ribbon Campaign" border="0"/></a>'
    print ''
    print '    <a href="http://www.openbsd.org/"><img'
    print '        src="../openbsd_pb.gif" alt="Powered by OpenBSD" border="0"/></a>'
    print '    <a href="http://validator.w3.org/check/referer"><img'
    print '        src="http://www.w3.org/Icons/valid-xhtml10"'
    print '        alt="Valid XHTML 1.0!" height="31" width="88" border="0" /></a>'
    print '  </td>'
    print '</tr>'
    print '</table>'
    print ''
    print '</body>'
    print '</html>'


if __name__ == "__main__":
    main()
