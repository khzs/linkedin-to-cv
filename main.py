import os
from time import sleep
from typing import OrderedDict
from pydantic_settings import BaseSettings
from playwright.sync_api import sync_playwright


class Settings(BaseSettings):
    output_path_stub: str = 'pages/output_'

settings = Settings()


def linkedin_to_txt(url_postfix: str = ''):
    current_section = url_postfix.split('/')[-2] if url_postfix.endswith('/') else url_postfix.split('/')[-1]
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False, channel="msedge")

        if os.path.exists("linkedin_auth.json"):
            context = browser.new_context(storage_state="linkedin_auth.json")
        else:
            context = browser.new_context()

        page = context.new_page()

        # Navigate directly to your profile
        page.goto('https://www.linkedin.com/in/me/' + url_postfix)

        # todo : networkidle takes too long, domcontentloaded doesn't load everything, this sleep is a hack but works
        page.wait_for_load_state('domcontentloaded')
        sleep(5)

        # If this is the first time, check if we got redirected to login
        current_url = page.url
        if '/login' in current_url or '/checkpoint' in current_url:
            print("Please log in manually...")
            print("Waiting for navigation to complete...")
            page.wait_for_url('**/in/me/**', timeout=120000)

            # Save the session for future use
            context.storage_state(path="linkedin_auth.json")
            print("Session saved!")

        text_content = page.inner_text('body')
        with open(settings.output_path_stub + current_section + '.txt', 'w', encoding='utf-8') as f:
            f.write(text_content)

        browser.close()


def process_txt() -> OrderedDict:
    dic = OrderedDict()

    with open('pages/output_contact-info.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if "Contact Info" in line:
                dic[lines[i + 1].strip()] = lines[i + 2].strip()
                dic[lines[i + 3].strip()] = lines[i + 4].strip()
                dic[lines[i + 5].strip()] = lines[i + 6].strip()
                break

    with open('pages/output_.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if "Retry for HUF0" in line:
                dic['Name'] = lines[i + 1].strip()
                dic['Headline'] = lines[i + 4].strip()
                break

    return dic


if __name__ == '__main__':
    # linkedin_to_txt()
    # linkedin_to_txt('overlay/contact-info/')
    data1 = process_txt()
    print(data1)
