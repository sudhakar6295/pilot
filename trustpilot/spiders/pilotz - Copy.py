from scrapy import Spider
from scrapy.http import Request

import json
import requests

from datetime import date
from datetime import timedelta
from pprint import pprint
import requests
import extruct
from w3lib.html import get_base_url


class PilotSpider(Spider):
    name = 'pilot'
    allowed_domains = ['nl.trustpilot.com']
    start_urls = ['https://nl.trustpilot.com/categories']
    

    def parse(self, response):
        
        categories=response.xpath('//*[@class="categories_categoryListObject__3WjQQ"]')
        #categories=categories[0:1]
        for category in categories:
            cate_url=category.xpath('.//a/@href').extract_first()
            c_type= category.xpath('.//*[@class="categories_categoryListItem__1dO4P"]/text()').extract_first()
            c_url=response.urljoin(cate_url)+'?numberofreviews=0&timeperiod=0'

            yield Request(c_url,callback=self.parse_category,meta={'c_type':c_type})

    

    def parse_category(self,response):
        try:
                c_type=response.meta['c_type']
                sub_categorys=response.xpath('//*[@class="styles_categoryBusinessListWrapper__2H2X5"]/a')
            
                for sub_cat in sub_categorys:
                    sub_url=sub_cat.xpath('.//@href').extract_first()
                    categories=sub_cat.xpath('.//*[@class="styles_categories__c4nU-"]/span/text()').extract_first()

                    s_url='https://nl.trustpilot.com'+sub_url

                    
                    try:
                            def get_html(url):
                                    """Get raw HTML from a URL."""
                                    headers = {
                                        'Access-Control-Allow-Origin': '*',
                                        'Access-Control-Allow-Methods': 'GET',
                                        'Access-Control-Allow-Headers': 'Content-Type',
                                        'Access-Control-Max-Age': '3600',
                                        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
                                    }
                                    req = requests.get(url, headers=headers)
                                    return req.text

                            def scrape(url):
                                    """Parse structured data from a target page."""
                                    html = get_html(url)
                                    metadata = get_metadata(html, url)
                                    return metadata

                                

                            def get_metadata(html, url):
                                    """Fetch JSON-LD structured data."""
                                    metadata = extruct.extract(
                                        html,
                                        base_url=get_base_url(html, url),
                                        syntaxes=['json-ld'],
                                    )['json-ld'][0]
                                    return metadata
                    except:
                        pass

                    res=scrape(s_url)
                    

                    info_url=''
                    try :
                        info=res['image'].replace('https://s3-eu-west-1.amazonaws.com/tpd/screenshotlogo-domain/','').replace('/198x149.png','').replace('https://s3-eu-west-1.amazonaws.com/tpd/screenshots/','')
                    except KeyError:
                        info=res['review'][0]['author']['url'].replace('https://nl.trustpilot.com/users/','')
                    except:
                        pass

                    info_url='https://nl.trustpilot.com/businessunit/'+info+'/companyinfobox'
                    if info_url:
                        
                        yield Request (info_url,callback=self.parse_details,meta={'c_type':c_type,'categories':categories})



                #Pagination
                next_page= response.xpath('//*[@name="pagination-button-next"]/@href').extract_first()
                if next_page:
                    abs_url='https://nl.trustpilot.com'+next_page
                    yield Request(abs_url,callback=self.parse_category,meta={'c_type':c_type})
        except:
            pass

    def parse_details(self,response):
        try:
                import json
                s=requests.get(response.url)
                
                result=json.loads(s.text)
            
                
                name=result["businessUnitDisplayName"]
                description=result["descriptionText"]
                categories=response.meta['categories']
                contact=result["contact"]
                Website=result["businessUnitWebsiteUrl"]


                email=contact["email"]
                phone=contact["phone"]
                address=contact["address"]
                zipcode=contact["zipCode"]
                city=contact["city"]
                country=contact["country"]
                category=response.meta['c_type']
                yield{ 'name':name,
                        'description':description,
                        'categories':categories,
                        'Website':Website,
                        
                        'category':category,
                        'address':address,
                        'email':email,
                        'phone':phone,
                        'address':address,
                        'zipcode':zipcode,
                        'city':city,
                        'country':country}
        except:
            pass

            

    
    

    
