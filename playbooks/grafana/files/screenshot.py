#! /usr/bin/env python3
#
# Copyright 2022  RedHat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

# A selenium wrapper to take OpenDev grafana screenshots in CI

import sys
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

out = sys.argv[1]
height = sys.argv[2]
url = sys.argv[3]

print("Getting %s -> %s" % (url, out))

firefox_options = webdriver.FirefoxOptions()

driver = webdriver.Remote(
    command_executor='http://localhost:4444/wd/hub',
    options=firefox_options)

driver.set_window_size(1920, height)
driver.get(url)

WebDriverWait(driver, 30).until(
    lambda driver: driver.execute_script(
        'return document.readyState') == 'complete')

# NOTE(ianw) : Grafana is a magic react app and I haven't found
# anything to reliably activate on other than just waiting a bit.
time.sleep(5)

driver.get_screenshot_as_file(out)

driver.quit()
