from time import sleep
from playwright.sync_api import sync_playwright
import os
import csv
from customtkinter import *
import json
import concurrent.futures
import subprocess



args=[
     '--disable-blink-features=AutomationControlled',
     '--start-maximized',
     '--disable-infobars',
     '--no-sandbox',
     '--disable-dev-shm-usage',
     '--disable-extensions',
     '--remote-debugging-port=0',
     '--disable-web-security',
     '--enable-features=WebRTCPeerConnectionWithBlockIceAddresses',
     '--force-webrtc-ip-handling-policy=disable_non_proxied_udp',
 ]

chrome_path = os.path.join(os.getcwd(), "chrome-win/chrome.exe")
# Define a function that opens the browser and returns the browser and contex
storage_state_file = os.path.join(os.getcwd(), "storage_state.json")
def is_storage_state_valid(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return bool(data)  # true false depend data exist
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return False
    else:
        open(file_path, 'w').close()  # Create an empty file
        return False

def cookie_save(login_status, log, close_event):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=str(chrome_path),
            headless=False,
            args=args,
        )
        if is_storage_state_valid(storage_state_file):
            context = browser.new_context(storage_state=storage_state_file, no_viewport=True)
        else:
            # If storage state is not valid, create a new context
            context = browser.new_context(no_viewport=True)

        page = context.new_page()
        page.goto("https://www.facebook.com/")

        # Check periodically whether the close_event is set
        while not close_event.is_set():
            # Perform any additional actions here if necessary
            pass
        # Save the storage state (including cookies)
        context.storage_state(path=storage_state_file)
        login_status.configure(text='Login Status : True')
        print("Login Data saved...")
        log.insert(END, "Login Data saved...\n")
        log.see(END)
        browser.close()


def stop_check(event, log) -> bool:
    if event:
        print("⏹️ Stoped...")
        log.insert(END, f"⏹️ Stoped...\n\n")
        log.see(END)
        return True
    else:
        return False


import concurrent.futures
import os


def scrapper_loop(all_group_url, message, file, sleeping, log, start, close_event):
        # Ensure storage state is valid
    if is_storage_state_valid(storage_state_file):
        all_link = all_group_url.splitlines()
        all_link = [x for x in all_link if len(x) > 0]
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=str(chrome_path),headless=False,args=args)
            context = browser.new_context(storage_state=storage_state_file, no_viewport=True)
            page = context.new_page()
            i = 1
            for url in all_link:
                print(f"No. {i} : {url}\n")
                log.insert(END, f"No. {i} : {url}\n")
                try:
                    page.goto(url)
                    page.wait_for_load_state('load')
                    # click to open posting
                    page.wait_for_selector("//span[normalize-space()='Write something...']", timeout=5000)
                    page.locator("//span[normalize-space()='Write something...']").click()

                    # write text
                    page.wait_for_selector("//div[@data-contents='true']", timeout=5000)
                    page.locator("//div[@data-contents='true']").fill(message)

                    file_path = os.path.join(os.getcwd(), file)
                    if file != "No file selected":
                        with page.expect_file_chooser() as fc_info:
                            page.click("(//div[@class='xr9ek0c xfs2ol5 xjpr12u x12mruv9'])[1]")
                            page.click("(//div[@class='x1sxyh0 xurb0ha']//div[@role='button'])[1]")
                            sleep(2)
                        file_chooser = fc_info.value
                        file_chooser.set_files(file_path)

                        if sleeping == "Sleep":
                            sleeping = "1"
                        sleep(int(sleeping))
                    page.click("(//div[@aria-label='Post'])[1]")
                    print(f"No. {i} Done...\n\n")
                    log.insert(END, f"No. {i} Done...\n\n")
                    sleep(2)
                except:
                    print(f"No. {i} Skipped...\n\n")
                    log.insert(END, f"No. {i} Skipped...\n\n")
                    pass
                i += 1
            browser.close()
        print(message)
        print(file)

        if not close_event.is_set():
            start.configure(text="▶️ Run")
            log.insert(END, f'\nDone.. All..\n')
            log.see(END)
    else:
        log.insert(END, 'Please login First..')
        log.see(END)

