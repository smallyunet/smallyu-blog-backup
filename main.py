# -*- coding:utf-8 -*-

import os
import logging
from unicodedata import name
import pdfkit
import requests
from bs4 import BeautifulSoup
import os.path
from PyPDF2 import PdfFileMerger
import shutil
import re

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>
{content}
</body>
</html>
"""

blog_url = "http://localhost:4000"

def get_url_list():
    response = requests.get(blog_url)
    soup = BeautifulSoup(response.content, "html.parser")
    menu_tag = soup.find_all(class_="list-group")[0]
    urls = []
    for li in menu_tag.find_all("li"):
        url = blog_url + li.a.get('href')
        urls.append(url)
    return urls


def parse_url_to_html(url, index):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        inner = soup.find_all(class_="inner")
        if inner.__len__() == 0:
            return ""
        body = inner[0]

        for img in body.find_all("img"):
            img_style = img.get("style")
            style = "display: block; margin-left: auto; margin-right: auto;"
            if img_style is not None:
                style += img_style
            img['style'] = style
        for v in body.find_all("h1"):
            v['style'] = "text-align: center;"
        for v in body.find_all(class_="time"):
            v['style'] = "text-align: center;"

        html = str(body)
        pattern = "(<img .*?src=\")(.*?)(\")"
        def func(m):
            return m.group(0).replace("src=\"", "src=\"" + url)
        html = re.compile(pattern).sub(func, html)
        html = html_template.format(content=html)

        tmpName = str(index) + ".html"
        tmpName = os.path.join("tmp_html", tmpName)
        with open(tmpName, 'wb') as f:
            f.write(html.encode())

        return tmpName

    except Exception as e:
        logging.error("parse error:", exc_info=True)


def save_pdf(htmls, file_name):
    options = {
        'page-size': 'B5',
        'margin-top': '15mm',
        'margin-right': '15mm',
        'margin-bottom': '15mm',
        'margin-left': '15mm',
        'encoding': "UTF-8",
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'minimum-font-size': 12,
    }
    try:
        pdfkit.from_file(htmls, file_name, options=options)
    except Exception as e:
        logging.error("covert error: ", exc_info=True)


def main():
    # os.mkdir("html") if not os.path.exists("html") else None
    # os.mkdir("pdf") if not os.path.exists("pdf") else None
    os.mkdir("tmp_html") if not os.path.exists("tmp_html") else None
    os.mkdir("tmp_pdf") if not os.path.exists("tmp_pdf") else None

    urls = get_url_list()
    pdfs = []
    for index, url in enumerate(urls):
        tmp_heml_name = parse_url_to_html(url, index)
        print("download index {} finished name {}".format(index, tmp_heml_name))

        if tmp_heml_name == "":
            continue

        tmp_pdf_name = tmp_heml_name.replace("html", "pdf")
        save_pdf(tmp_heml_name, tmp_pdf_name)
        pdfs.append(tmp_pdf_name)

        print("convert index {} finished name {}".format(index, tmp_pdf_name))

    merger = PdfFileMerger()
    for pdf in pdfs:
        merger.append(open(pdf, 'rb'))
        print("merge index {} finished name {}".format(index, pdf))

    output = open(u"smallyu_blog_backup.pdf", "wb")
    merger.write(output)

    # shutil.rmtree("tmp_html")
    # shutil.rmtree("tmp_pdf")


if __name__ == '__main__':
    main()
