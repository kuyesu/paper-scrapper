print("Initiating... please wait.\n")

import requests
import csv
import re
import random
import time
import pandas as pd
from sys import exit
from bs4 import BeautifulSoup

# ===== DEFINE FUNCTIONS =====

search_from, URL_edit = "", ""


def wait():
    print("Waiting for a few secs...")
    time.sleep(random.randrange(1, 6))
    print("Waiting done. Continuing...\n")


def checkPage():
    global search_from
    if "scholar.google.com" in URL_input:
        search_from = "Google Scholar"
        print("Input is from: Google Scholar.\n")
    elif "pubmed" in URL_input:
        search_from = "Pubmed"
        print("Input is from: PubMed.\n")
    elif "sciencedirect.com" in URL_input:
        search_from = "Science Direct"
        print("Input is from: Science Direct.\n")
    elif "plos.org" in URL_input:
        search_from = "PLOS"
        print("Input is from: PLOS.\n")

    else:
        print("Page URL undefined.\n")


# ===== GETTING AND SETTING THE URL =====

URL_input = input("Please paste search URL and press Enter:")
URL_ori = URL_input
headers = requests.utils.default_headers()
headers.update(
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    }
)
checkPage()


# ===== MAIN FRAMEWORK =====


try:

    # SETTING UP THE CSV FILE

    outfile = open("scrapped_science_direct.csv", "w", newline="", encoding="utf-8")
    writer = csv.writer(outfile)
    df = pd.DataFrame(
        columns=["Title", "Article Rype", "Year", "Source", "Authors", "Link"]
    )

    # SETTING & GETTING PAGE NUMBER

    page_num = 0
    offset = 0
    page_view = 100
    URL_edit = str(URL_ori + "&show=" + str(page_view) + "&offset=" + str(offset))

    page = requests.get(URL_edit, headers=headers, timeout=None)
    soup = BeautifulSoup(page.content, "html.parser")
    wait()

    search_results = soup.find_all("span", class_="search-body-results-text").text
    print(search_results)

    if "About" in search_results:
        search_results_split = search_results.split("results")[0].split("About")[1]
    elif "results" in search_results:
        search_results_split = search_results.split("results")[0]
    else:
        seascrapped_science_directrch_results_split = search_results.split("result")[0]

    search_results_num = int("".join(filter(str.isdigit, search_results_split)))
    page_total_num = int(search_results_num / 10) + 1
    print(f"Total page number: {page_total_num}")
    print(f"Total search results: {search_results_num}.\n")

except AttributeError:

    print("Opss! ReCaptcha is probably preventing the code from running.")
    print("Please consider running in another time.\n")
    # exit()
    wait()

wait()

# # EXTRACTING INFORMATION

for i in range(page_total_num):

    # SETTING UP URL SECOND TIME

    page_num_up = page_num + i
    print(f"Going to page {page_num_up}.\n")
    URL_edit = str(URL_ori + "&show=" + str(page_view) + "&offset=" + str(page_num_up))
    wait()
    # if page_num_up != 2 and page_num_up != 1:
    # 	# time.sleep(2)
    headers = requests.utils.default_headers()
    headers.update(
        {
            "User-Agent": "Mozilla/15.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20210916 Firefox/95.0",
        }
    )

    page = requests.get(URL_edit, headers=headers, timeout=None)
    soup = BeautifulSoup(page.content, "html.parser")
    wait()
    response = requests.get(URL_edit, headers=headers)

    # check successful response
    if response.status_code != 200:
        print("Status code:", response.status_code)
        raise Exception("Failed to fetch web page ")

    results = soup.find("div", id="srp-results-list")
    paper_doc = BeautifulSoup(response.text, "html.parser")

    # EXTRACTING INFORMATION

    try:

        job_elements = results.find_all("div", class_="result-item-content")
        for job_element in job_elements:
            try:
                article_type = job_element.find(
                    "span", class_="article-type u-clr-grey8"
                ).text
                article_title = job_element.find("span", class_="anchor-text").text
                article_src = job_element.find(
                    "span", class_="srctitle-date-fields"
                ).text
                article_authors = job_element.find(
                    "ol", class_="Authors hor reduce-list"
                ).text
                article_date = article_src.split(",")[-2]
                source = article_src.split(",")[:-1]
                links = job_element.find(
                    "a", class_="anchor download-link anchor-default"
                )
                link_url = links["href"]

            except Exception as e:
                print(e)
                continue
            print(article_title)

            df2 = pd.DataFrame(
                [
                    [
                        article_title,
                        article_type,
                        article_date,
                        source,
                        article_authors,
                        link_url,
                    ]
                ],
                columns=[
                    "Title",
                    "Cites",
                    "Year",
                    "Reference",
                    "Publisher",
                    "Tag",
                    "Link",
                    "Description",
                ],
            )
            df = pd.concat([df, df2], ignore_index=True)
            headers = ["Title", "Article Rype", "Year", "Source", "Authors", "Link"]

            with open(
                "scrapped_science_direct.csv", "a", newline="", encoding="utf-8"
            ) as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        article_title,
                        article_type,
                        article_date,
                        source,
                        article_authors,
                        link_url,
                    ]
                )

            # time.sleep(1)
    except AttributeError:
        print("Opss! ReCaptcha is probably preventing the code from running.")
        print("Please consider running in another time.\n")
        # exit()
        wait()

df.index += 1
df.to_csv("scrapped_gscholar.csv", encoding="utf-8")
outfile.close()

# ===== CODE FOR SCIENCE  =====

# END OF PROGRAM

print("Job finished, Godspeed you! Cite us.")
