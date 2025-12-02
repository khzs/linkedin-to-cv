import os
from playwright.sync_api import sync_playwright


def linkedin_to_something():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False, channel="msedge")

        if os.path.exists("linkedin_auth.json"):
            context = browser.new_context(storage_state="linkedin_auth.json")
        else:
            context = browser.new_context()

        page = context.new_page()

        # Navigate directly to your profile
        page.goto('https://www.linkedin.com/in/me/')

        # Wait for page to load
        page.wait_for_load_state('domcontentloaded')

        # If this is the first time, check if we got redirected to login
        current_url = page.url
        if '/login' in current_url or '/checkpoint' in current_url:
            print("Please log in manually...")
            print("Waiting for navigation to complete...")
            page.wait_for_url('**/in/me/**', timeout=120000)

            # Save the session for future use
            context.storage_state(path="linkedin_auth.json")
            print("Session saved!")



        browser.close()


if __name__ == '__main__':
    linkedin_to_something()
