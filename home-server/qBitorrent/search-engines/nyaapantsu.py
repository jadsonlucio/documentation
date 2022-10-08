#VERSION: 1.05
#AUTHORS: Eugene (xux@live.ca)

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the author nor the names of its contributors may be
#      used to endorse or promote products derived from this software without
#      specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

try:
    # python3
    from html.parser import HTMLParser
except ImportError:
    # python2
    from HTMLParser import HTMLParser

from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file

class nyaapantsu(object):
    url = 'https://nyaa.pantsu.cat'
    name = 'NyaaPantsu'
    supported_categories = {'all': '0_0', 
                            'software': '1_1', 
                            'games': '1_2', 
                            'music': '2_0', 
                            'anime': '3_0', 
                            'books': '4_0', 
                            'tv': '5_0', 
                            'pictures': '6_0'}
    
    class NyaaPantsuParser(HTMLParser):
        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url
            self.has_nestPage = False
            self.url_nextPage = None
            self.current_item = None
            self.do_parse = False
            self.do_save_data = None
            self.td_ctr = None
            
        
        def handle_starttag(self, tag, attrs):
            if tag == 'tr':
                self.handle_start_tag_tr(attrs)
            elif tag == 'td':
                self.handle_start_tag_td(attrs)
            elif tag == 'a':
                self.handle_start_tag_a(attrs)
        
        def handle_start_tag_tr(self, attrs):
            tr_attrList = dict(attrs)
            if 'class' in tr_attrList:
                if tr_attrList['class'].startswith('torrent'):
                    self.current_item = {"engine_url" : self.url}
                    self.do_parse = True
                    self.td_ctr = 0
                    self.current_item['size'] = 'Unkown'
                    self.current_item['seeds'] = 'Unkown'
                    self.current_item['leech'] = 'Unkown'
        
        def handle_start_tag_td(self, attrs):
            td_attrList = dict(attrs)
            if td_attrList['class'].startswith('tr-size'):
                self.do_save_data = 'size'
            if td_attrList['class'].startswith('tr-se'):
                self.do_save_data = 'seeds'
            if td_attrList['class'].startswith('tr-le'):
                self.do_save_data = 'leech'
        
        def handle_start_tag_a(self, attrs):
            a_attrList = dict(attrs)
            if 'id' in a_attrList:
                if a_attrList['id'] == 'page-next':
                    self.has_nestPage = True
                    self.url_nextPage = self.url + a_attrList['href'].strip()
            if self.do_parse:
                if a_attrList['href'].startswith('/view'):
                    self.current_item['desc_link'] = self.url + a_attrList['href'].strip()
                    self.do_save_data = 'name'
                if a_attrList['href'].startswith('magnet'):
                    self.current_item['link'] = a_attrList['href'].strip()
        
        def handle_data(self, data):
            if self.do_parse:
                if self.do_save_data != None:
                    if self.do_save_data not in self.current_item:
                        self.current_item[self.do_save_data] = ''
                    self.current_item[self.do_save_data] = data.strip()
                    self.do_save_data = None
        
        def handle_endtag(self, tag):
            if tag == 'tr' and self.do_parse:
                prettyPrinter(self.current_item)
                self.current_item = None
                self.td_ctr = None
                self.do_parse = False
            
    def download_torrent(self, info):
        print (download_file(info))
    
    def search(self, what, cat='all'):
        searchPage = retrieve_url(self.url + '/search?c=' + self.supported_categories[cat] + '&q=' + what.replace("%20", "+"))
        parser = self.NyaaPantsuParser(self.url)
        parser.feed(searchPage)
        parser.close()
        
        while parser.has_nestPage:
            parser.has_nestPage = False
            parser.feed(retrieve_url(parser.url_nextPage))
            parser.close()
        