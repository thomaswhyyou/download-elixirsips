import shutil
import logging

import click
import requests
import lxml.html


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT_URL = "https://elixirsips.dpdcart.com"
LOGIN_PATH = "/subscriber/login"


@click.command()
@click.option('--username', prompt='Username')
@click.option('--password', prompt='Password')
def hello(username, password):
    login_url = ROOT_URL + LOGIN_PATH

    data = {
        "username": username,
        "password": password,
    }

    s = requests.Session()
    s.get(login_url)
    res = s.post(login_url, data=data)

    root = lxml.html.fromstring(res.content)
    nodes = root.find_class("content-post-meta")
    hrefs = [n.find(".//span/a").attrib.get("href") for n in nodes]

    for epath in hrefs:
        ep = s.get(ROOT_URL + epath)
        ep_root = lxml.html.fromstring(ep.content)
        dl_links = ep_root.xpath(".//a[starts-with(@href, '/subscriber/download')]")

        for el in dl_links:
            fpath = el.attrib.get("href")
            r = s.get(ROOT_URL + fpath, stream=True)
            if r.status_code != 200:
                continue

            with open(el.text, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)


if __name__ == '__main__':
    hello()
