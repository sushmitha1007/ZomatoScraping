from enum import IntEnum
from selenium import webdriver
import crochet
from starlette.datastructures import Address
crochet.setup()
from datetime import date, datetime
import pandas as pd
from scrapy.crawler import CrawlerRunner
import time
from typing import List
import os
from fastapi import FastAPI,Form,UploadFile,File
from pydantic import BaseModel
from openpyxl import load_workbook
import codecs
import re
from gmbcontractscraper.config.constants import OUTPUT_FOLDERNAME
from gmbcontractscraper.utils.dropboxFileUpload_scraper import upload_to_dropbox_scrapy
# from logs import create_error_log
app = FastAPI()

output_data = []

crawl_runner = CrawlerRunner()

# For Headless Browser
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)" \
             " Chrome/89.0.4389.114 Safari/537.36"
options = webdriver.ChromeOptions()
options.headless = True
options.add_argument(f'user-agent={user_agent}')
options.add_argument("--window-size=1920,1080")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')
options.add_argument("--disable-extensions")
options.add_argument("--proxy-server='direct://'")
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--start-maximized")
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_argument('--disable-popup-blocking')
driver = webdriver.Chrome(executable_path = "./chromedriver", options = options)


# driver = webdriver.Chrome("./chromedriver")
# class ScrapeData(BaseModel):
#     urls : List

@app.post('/restaurants/')
def upload_file_n_scraping(fileb:UploadFile = File(...)):
#    print(urls)
    
    contents = fileb.file.read()
        # return contents
    byte_to_string = codecs.decode(contents, "utf-8")  # convert byte to string
    # return byte_to_string
    regex = re.compile(r'[\r\t]')
    string = regex.sub(" ", byte_to_string)
    # remove_first_line = string[9:]
    output = string.split(" \n")
    del output[0]
    # return output
    for i in range(len(output) - 1):
        Name =[]
        Cuisines = []
        address =[]
        dining_review = []
        delivery_review =[]
        timings = []
        full_address = []
        phone_number = []
        fssai = []
        items = []
        
        rates = []
        driver.get(output[i]) 
        time.sleep(2)
        try:
            name = driver.find_element_by_xpath('//*[@id="root"]/div/main/div/section[3]/section/section/div/div/div/h1').text
            print("Name: ", name)
            Name.append(name)
        except:
            Name.append("Name not found")
        try:
            listvalues = driver.find_elements_by_xpath('//section[@class="sc-qrIAp bRNNbu"]')
            hotels_list = []
            for p in range(len(listvalues)):
                hotels_list.append(listvalues[p].text)
            hotels_list = hotels_list[0].split('\n')
            cuisines = hotels_list[0]
            Address = hotels_list[1]
            print("Cuisines: ",cuisines)
            print("address: ",Address)
            Cuisines.append(cuisines)
            address.append(Address)
        except:
            Cuisines.append("Cusines not found")
            address.append("Address not found")
        try:
            Dining_review = driver.find_element_by_xpath('//*[@id="root"]/div/main/div/section[3]/section/section/div/div/div/section/div[1]/div[1]/div/div/div[1]').text
            print("dining_review: ",Dining_review)
            dining_review.append(Dining_review)
        except Exception as e:
            dining_review.append("dining review not found")
        try:
            Delivery_review = driver.find_element_by_xpath('//*[@id="root"]/div/main/div/section[3]/section/section/div/div/div/section/div[3]/div[1]/div/div/div[1]').text
            print("delivery_review: ",Delivery_review)
            delivery_review.append(Delivery_review)
        except Exception as e:
            delivery_review.append("Delivery review not found")
        try:
            Timings = driver.find_element_by_xpath('//*[@id="root"]/div/main/div/section[3]/section/section/div/div/section[2]/section/span').text
            print("timings: " , Timings)
            timings.append(Timings)
        except:
            timings.append("Timings not found")
        driver.find_element_by_xpath('//*[@id="TabLink__0"]/a').click()
        time.sleep(20)
        try:
            article_split = driver.find_element_by_xpath('//article[@class="sc-doZvUO dqIQhP"]')
            print(type(article_split))
            phone_list = article_split.text.split('\nDirection\nⒸ OpenStreetMap contributors\n')
            Full_address = phone_list[1].split('\nCopy\nDirection')
            Phone_number = phone_list[0]
            Phone_number = Phone_number[6:]
            Full_address = Full_address[0]
            Phone_number = Phone_number.replace('\n'," ,")
            print("full_address : ",Full_address)
            print("phone_number: ",Phone_number)
            full_address.append(Full_address)
            phone_number.append(Phone_number)
        except:
            full_address.append("Address not found")
            phone_number.append("Phone number not found")
        driver.find_element_by_xpath('//*[@id="TabLink__1"]/a').click()
        time.sleep(2)
        try:
            ss = driver.find_elements_by_xpath('//h4[@class="sc-1s0saks-15 iSmBPS"]')
            # print(ss)
            hotels_list123 = []
            for p in range(len(ss)):
                items.append(ss[p].text)
        # print(hotels_list123
        #)
            print(len(items))
        except:
            items.append("not found")

        
        try:
            ss2 = driver.find_elements_by_xpath('//span[@class="sc-17hyc2s-1 cCiQWA"]')
            # list2 = []
            for r in range(len(ss2)):
                rates.append(ss2[r].text)
            # print(list2)
            print(len(rates))
        except:
            rates.append("not found")
        try:
            Fssai = driver.find_element_by_xpath('//p[@class="sc-eetwQk eoLDmz"]').text
            fssai.append(Fssai)
        except Exception as e:
            fssai.append("fssai not found")
        my_dict = {'Name': Name, 'Cuisines':Cuisines,'Address' : address,'Dining_review':dining_review,"Delivery_review":delivery_review,
        'timings':timings,'Full_address':full_address,'Phone_number':phone_number,"fssai":fssai
            }
        rest_menu = {"items":items, "rates":rates}
    
        df = pd.DataFrame(my_dict)
        df1 = pd.DataFrame(rest_menu)  # Initialize every field with the resultant array
        file_path = os.path.join(os.getcwd(), 'output',f"{name}{str(date.today())}.xlsx")
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
        
        df.to_excel(writer, sheet_name = 'Resturant')
        # writer.save()
    
        sheet_name1 = f"x{i}"
        
        print("sheet_name1:" ,sheet_name1)
        df1.to_excel(writer, sheet_name = "Menu")
        
        # pd.concat()
        writer.save()
        # writer.close()
        # rates.clear()
        # items.clear()
        print("saved Successfully")
