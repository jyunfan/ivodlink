#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Collect video links from ivod.ly.gov.tw """
import re
from urllib import urlencode

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest
from ivodlink.items import IvodlinkItem

class IvodSpider(CrawlSpider):
    name = 'ivodlink'
    allowed_domains = ['ivod.ly.gov.tw']

    rules = [
            Rule(SgmlLinkExtractor(
                allow = ('new_vod_1t.jsp\?keyWord=')),
                callback = 'parse_list'),
    ]

    def __init__(self, startyear=2012, startmonth=1, startday=1,
                       endyear=2012,   endmonth=12,  endday=31):
        request = {'keyWord':'',
          'commissionerName':'',
          'film':'c',
          'select_type':'time',
          'period':3,
          'startyear':startyear,
          'startmonth':startmonth,
          'startday':startday,
          'endyear':endyear,
          'endmonth':endmonth,
          'endday':endday,
          'select1':8,
          'select2':1,
          'select3':0,
          'udlang':'ch',
          'as_fid':6}
        self.start_urls = ['http://ivod.ly.gov.tw/new_vod_1t.jsp?' +
            urlencode(request)]

        super(CrawlSpider, self).__init__()
        self._compile_rules()

    def parse_list(self, response):
        self.log('crawl: %s' % response.url)
        hxs = HtmlXPathSelector(response)
        items = hxs.select('//tr[(child::td/table/tr/td/img)]')

        for item in items:
            # description has onmouseover pattern
            desc = item.select(".//tr[@onmouseover='this.bgColor=\"#FFFFCC\";']")
            if desc:
                tags = item.select('.//*[not(@class="file_no" or self::caption)]/text()').extract()
                voddesc = '\n'.join([t.strip() for t in tags if t.strip()])
                continue

            vods = item.select(".//a[contains(@href,'new_vod_1t.jsp?CLIP_NAME=tw/wmv-clip/')]/@href").extract()
            if not vods:
                continue

            #self.log('Request %s' % vods[0])
            # Every video has 2 versions.  We need only the first, high quality, one.
            requrl = (u'http://ivod.ly.gov.tw/%s' % vods[0]).encode('big5')
            yield Request(requrl,
                    meta={'desc':voddesc},
                    callback=self.parse_play,
                    errback=self.errback)

    def errback(self):
        self.log('Request failed')

    def parse_play(self, response):
        #self.log('Play page %s' % response.url)
        hxs = HtmlXPathSelector(response)
        item = IvodlinkItem()
        item['url'] = hxs.select("//embed/@src").extract()[0]
        if item['url'].find('YYYY') > 0:
            self.log('Skip invalid mms link: YYYY-MM-DD-HH-MM')
            return
        item['description'] = response.meta['desc']
        item['date'] = re.search('\d{4}-\d{2}-\d{2}', item['description']).group()
        return item

