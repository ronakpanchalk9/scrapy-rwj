import scrapy
from penguin_assessment.items import PenguinAssessmentItem
from datetime import datetime
from scrapy.http import FormRequest, Request
from scrapy import Selector
import json



class PenguinSpider(scrapy.Spider):
    name = "ronak_spider"
    allowed_domains = ["rewardsforjustice.net"]

    output_filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    custom_settings = {
        "FEEDS": {
            f"{output_filename}.json": {"format": "json"},
            f"{output_filename}.csv": {"format": "csv"},
        }
    }

    def start_requests(self):
        url = "https://rewardsforjustice.net/index/?jsf=jet-engine:rewards-grid&tax=crime-category:1070%2C1071%2C1073%2C1072%2C1074"
        formdata={
                    "action":"jet_engine_ajax",
                    "handler":"get_listing",
                    "page_settings[post_id]":"22076",
                    "page_settings[queried_id]": "22076|WP_Post",
                    "page_settings[element_id]":"ddd7ae9",
                    "page_settings[page]":"1",
                    "listing_type":"elementor",
                    "isEditMode":"false",
                    "addedPostCSS[]":"22078"
                }
        return [scrapy.FormRequest(url, formdata=formdata, callback=self.logged_in)]

    def parse_item(self, response):
        details = PenguinAssessmentItem()
        details['page_url'] = response.url

        try: details['title'] = response.xpath('//*[@id="hero-col"]/div/div[1]/div/h2/text()')[0].get()
        except: details['title'] = 'null'

        try: details['rewarded_amount'] = response.xpath('//*[@id="reward-box"]/div/div[2]/div/h2/text()')[0].get()
        except: details['rewarded_amount'] = 'null'

        try: details['associated_org'] = response.xpath('string(//*[@id="Rewards-Organizations-Links"]/div)').get().split(':')[1]
        except : details['associated_org'] = 'null'
        if details['associated_org']:
            details['associated_org'] = details['associated_org'].replace('\n', '').replace('\t', '')

        try: details['associated_loc'] = response.xpath('//*[@id="reward-fields"]/div/div[5]/div/div/span/text()')[0].get()
        except: details['associated_loc'] = 'null'

        details['about'] = response.xpath('string(//*[@id="reward-about"]/div/div[2]/div)').get()
        details['image_url'] = response.xpath('//*[@id="gallery-1"]/figure/div/img/@src').extract()
        if not details['image_url']:
            details['image_url'] = response.xpath('//*[@id="gallery-1"]/figure/div/picture/img/@src').extract()

        details['category'] = self.category

        details['dob'] = response.xpath('//div[@class = "elementor-element elementor-element-9a896ea dc-has-condition dc-condition-empty elementor-widget elementor-widget-text-editor"]/div/text()').get()
        if details['dob'] :
            details['dob'] = details['dob'].replace('\n', '').replace('\t', '')

        return details
    
    def logged_in(self, response):
        dict_response = json.loads(response.text)
        # print(dict_response['data']['html'])
        res_html = dict_response['data']['html']
        max_num_pages = dict_response['data']['filters_data']['props']['rewards-grid']['max_num_pages']
        page = dict_response['data']['filters_data']['props']['rewards-grid']['page']
        found_posts = dict_response['data']['filters_data']['props']['rewards-grid']['found_posts']
        selector_elm = Selector(text=res_html)
        self.category = selector_elm.xpath('.//h2[@class="elementor-heading-title elementor-size-default"]/text()').get()

        for url in selector_elm.xpath('.//a[@class="jet-engine-listing-overlay-link"]/@href'):
            yield scrapy.Request(response.urljoin(url.get()), callback=self.parse_item)
        
        if page < max_num_pages:
            url = 'https://rewardsforjustice.net/index/?jsf=jet-engine:rewards-grid&tax=crime-category:1070%2C1071%2C1073%2C1072%2C1074'
            url = url + '&pagenum=' + str(page+1)
            form_data = {'action': 'jet_engine_ajax',
                'handler': 'get_listing',
                'page_settings[post_id]' : '22076',
                'page_settings[queried_id]': '22076|WP_Post',
                'page_settings[element_id]': 'ddd7ae9',
                'page_settings[page]' : '1',
                'listing_type' : 'elementor',
                'isEditMode' : 'false',
                'addedPostCSS[]' : '22078'
            }

        yield scrapy.FormRequest(url,formdata=form_data,callback=self.logged_in)