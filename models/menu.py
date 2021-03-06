# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(IMG(_src=URL('static','images/logo.png'), _alt="thumbs", _width="35px",_height="30px"),_class="brand",_href=URL('index'))
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Your Name <you@example.com>'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = []

DEVELOPMENT_MENU = True

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    response.menu += [
        (SPAN('Takes', _class='highlighted'), False, '', [
        (T('Submit Take'), False, URL('takes','submitTake')),
        (T('General Feed'), False, URL('takes','generalFeed')),
        (T('Subscription Feed'), False, URL('takes','subscriptionFeed')),
        (T('Topic Feed'), False, URL('takes','topicPage'), [
                        ('Entertainment', False,
                         URL('takes','topicFeed',vars=dict(topicId='1'))),
                        (T('Sports'), False,
                         URL('takes','topicFeed',vars=dict(topicId='6'))),
                        (T('Revanth :P'),
                         False, URL('takes','subscriptionFeed')),
                        ])
                ]
         )]
if DEVELOPMENT_MENU: _()
