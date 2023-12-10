import re

from bs4 import BeautifulSoup
from urllib3.util import parse_url

from module.network import RequestContent
from module.utils import save_image


def mikan_parser(homepage: str):
    root_path = parse_url(homepage).host
    with RequestContent() as req:
        content = req.get_html(homepage)
        soup = BeautifulSoup(content, "html.parser")
        poster_div = soup.find("div", {"class": "bangumi-poster"}).get("style")
        title = soup.select_one(
            'p.bangumi-title a[href^="/Home/Bangumi/"]'
        )
        if title is None:
            title = soup.select_one(
                'p.bangumi-title'
            )
        official_title = title.text
        official_title = re.sub(r"第.*季", "", official_title).strip()
        year = get_year(soup)
        if poster_div:
            poster_path = poster_div.split("url('")[1].split("')")[0]
            img = req.get_content(f"https://{root_path}{poster_path}")
            suffix = poster_path.split(".")[-1]
            poster_link = save_image(img, suffix)
            return poster_link, official_title, year
        return "", "", ""


def get_year(soup: BeautifulSoup) -> str:
    infos = soup.select(
        'p.bangumi-info'
    )
    if len(infos) == 0:
        return ""
    for info in infos:
        text = info.text
        if text.startswith('放送开始：'):
            s = text.split('/')
            if len(s) == 0:
                continue
            year = s[-1]
            if year.isdigit() and len(year) == 4:
                return year
    return ""
