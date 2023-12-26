
from playwright.sync_api import sync_playwright, Playwright
import os
from scrapy.selector import Selector
import json
import re
import time
import random


def run(playwright: Playwright):
    firefox = playwright.firefox
    browser = firefox.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://ixiporn.cc/")
    page.wait_for_selector("//div[@data-post-id]",timeout= 5*60*1000)
    context.storage_state(path="state.json")
    context.close()
    page.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)