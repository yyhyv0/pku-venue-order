# -*- coding: utf-8
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import base64
import numpy as np
import re

class Browser():
    def __init__(self):
        chrome_options=Options()
        # chrome_options.add_argument('--headless')
        self.browser = webdriver.Chrome(chrome_options=chrome_options,executable_path="C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")

    def sildeBarByXPath(self, xpath, slideDist):
        swiper = self.browser.find_element_by_xpath(xpath) 
        action = webdriver.ActionChains(self.browser)
        action.click_and_hold(swiper).perform() 
        action.move_by_offset(slideDist,0).perform() # silde
        action.release().perform()

    def getDecodedRawImageByXPath(self, xpath):
        imgRaw = self.browser.find_element_by_xpath(xpath).get_attribute('src')
        imgBase64 = re.sub('^data:image/.+;base64,', '', imgRaw)
        imgData = base64.b64decode(imgBase64)
        return np.fromstring(imgData, np.uint8)        
        
    def clickByXPath(self, xpath):
        while True:
            try:
                self.browser.find_element_by_xpath(xpath).click()
                return
            except Exception as e:
                # print(e)
                pass

    def clickByCssSelector(self, cssSelector):
        while True:
            try:
                self.browser.find_element_by_css_selector(cssSelector).click()
                return
            except Exception as e:
                # print(e)
                pass

    def typeByCssSelector(self, cssSelector, text):
        while True:
            try:
                self.browser.find_element_by_css_selector(cssSelector).clear()
                self.browser.find_element_by_css_selector(cssSelector).send_keys(text)
                return
            except Exception as e:
                # print(e)
                pass

    def typeByXPath(self, xpath, text):
        while True:
            try:
                self.browser.find_element_by_xpath(xpath).clear()
                self.browser.find_element_by_xpath(xpath).send_keys(text)
                return
            except Exception as e:
                # print(e)
                pass

    def findElementByXPath(self, xpath):
        while True:
            try:
                element = self.browser.find_element_by_xpath(xpath)
                return element
            except Exception as e:
                # print(e)
                pass

    def findElementByCssSelector(self, cssSelector):
        while True:
            try:
                element = self.browser.find_element_by_css_selector(cssSelector)
                return element
            except Exception as e:
                # print(e)
                pass

    def gotoPage(self, url):
        print("goto page %s" % url)
        self.browser.execute_script("window.open(\"%s\")" % url)
        self.browser.switch_to.window(self.browser.window_handles[-1])

    def close(self):
        try:
            self.browser.quit()
            self.browser.close()
        except:
            pass