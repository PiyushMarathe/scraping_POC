import os
import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.crawler import CrawlerProcess
from scrapy import Request
import json
import smtplib
#import boto3

EMAIL_ADDRESS = 'marathe.piyush295@gmail.com' #os.environ.get('EMAIL_USER')
EMAIL_PASS = 'vhwemkjejepplzjp' #os.environ.get('EMAIL_PASSWORD')


def notification():
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASS)

        subject = 'Important! Attention Required regarding update'
        body = 'It seems there is some update in the fields of the website you are trying to access'

        msg = f'Subject: {subject}\n\n\n{body}'

        smtp.sendmail(EMAIL_ADDRESS, 'piyushpm295@gmail.com', msg)
        print("Mail sent")


def compare(dict, file):
    config_file = (os.path.join(os.getcwd(), "Config", file+".json"))
    file1 = open(config_file, )
    config_file_data = json.load(file1)
    url = config_file_data['url']
    file1.close()
    output_file_data = dict
    s = set()
    s1 = set()
    status = True
    for key in output_file_data.keys():
        for key1 in config_file_data['data'].keys():
            if key not in config_file_data['data'].keys() and key1 not in output_file_data.keys():
                s.add(key)
                s1.add(key1)
                print(f"Old field -{s} is modified to new field-{s1}")
                print(f"Difference detected in {url}  in {file} court website!")
                mess = f"Difference detected in {url}  in {file} court website!"
                f"Old field -{key} is modified to new field-{key1},\nKindly visit the website for more information"
            # code for sending Notification
                # notification()
                status = False
        else:
            print("MATCHING", key)
    if status:
        return True
    else:
        mess=f"Old field -{s} is modified to new field-{s1}"
        print(mess)
        sns_client = boto3.client('sns')
        sns_client.publish(
            TargetArn='arn:aws:sns:us-east-2:478750502411:NotificationSNS',
            Message=mess,
            Subject=f'Difference detected in {url}  in {file} court website!')
        return False


class LkSpider(CrawlSpider):
    name = 'multi_spider'

    # start_urls =['https://www.worldometers.info/world-population/population-by-country/','http://econpy.pythonanywhere.com/ex/001.html/']
    def start_requests(self):
        files = os.listdir((os.path.join(os.getcwd(), "Config")))
        for file in files:
            file_name = (os.path.join(os.getcwd(), "Config", file))
            f = open(file_name, )
            data_value = json.load(f)
            f.close()
            config_url = data_value['url']
            # Pagination_process_for yielding_URL
            yield scrapy.Request(url=config_url, callback=self.parse)

    def parse(self, response):
        files = os.listdir((os.path.join(os.getcwd(), "Config")))
        for file in files:
            if file.split('.')[0] in (str(response)):
                file_name = (os.path.join(os.getcwd(), "Config", file))
                f = open(file_name, )
                data_value = json.load(f)
                f.close()
                config_data=data_value['data']
                scraping=data_value['scraping']
            else:
                continue
            dictionary = {}
            counter = 0
            for i in config_data.values():
                buyers=response.xpath("{}{}/text()".format(i,scraping)).extract()
                item_prices=response.xpath("{}/text()".format(i)).getall()
                dictionary[''.join(map(str, buyers[0]))]=''.join(map(str,item_prices))
                counter += 1
            filename=file.split('.')[0]+"_data.json"
            if compare(dictionary,file.split('.')[0]):
                with open(filename, 'w') as f:
                    json.dump(dictionary, f)
            yield dictionary


# main driver
if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(LkSpider)
    process.start()






