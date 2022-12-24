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

# ===== CODE FOR PUBMED =====

if search_from == "Pubmed":

    try:

        # SETTING UP THE CSV FILE

        outfile = open("scrapped_pubmed.csv", "w", newline="", encoding="utf-8")
        writer = csv.writer(outfile)
        df = pd.DataFrame(
            columns=[
                "Title",
                "Cites",
                "Year",
                "Reference",
                "Publisher",
                "Tag",
                "Link",
                "Description",
            ]
        )

        # SETTING & GETTING PAGE NUMBER

        page_num = 1
        page_view = 100  # can be change to 10, 20, 50, 100 or 200
        URL_edit = URL_ori + "&page=" + str(page_num) + "&size=" + str(page_view)
        print("URL : ", URL_edit)
        # URL_edit = "https://pubmed.ncbi.nlm.nih.gov/?term=machine+learning+and+diabetic+retinopathy+classification+or+diagnosis"

        page = requests.get(URL_edit, headers=headers, timeout=None)
        soup = BeautifulSoup(page.content, "html.parser")
        wait()
        # print("Page number: ", page_num)
        # print(soup.prettify())
        page_total = soup.find("label", class_="of-total-pages").text
        page_total_num = int("".join(filter(str.isdigit, page_total)))
        print(f"Total page number: {page_total_num}")
        print(f"Results per page: {page_view}.\n")

    except AttributeError:

        print("Opss! ReCaptcha is probably preventing the code from running.")
        print("Please consider running in another time.\n")
        # exit()
        wait()

    wait()

    # EXTRACTING INFORMATION

    for i in range(page_total_num):

        page_num_up = 20 + i
        URL_edit = URL_ori + "&page=" + str(page_num_up) + "&size=" + str(page_view)
        page = requests.get(URL_edit, headers=headers, timeout=None)

        soup = BeautifulSoup(page.content, "html.parser")
        wait()
        results = soup.find("section", class_="search-results-list")

    try:

        # EXTRACTING INFORMATION

        job_elements = results.find_all("article", class_="full-docsum")

        for job_element in job_elements:
            title_element = job_element.find("a", class_="docsum-title")
            cit_element = job_element.find(
                "span", class_="docsum-journal-citation full-journal-citation"
            ).text.strip()
            description = job_element.find(
                "div", class_="full-view-snippet"
            ).text.strip()
            authors = job_element.find(
                "span", class_="docsum-authors full-author"
            ).text.strip()
            year = cit_element.split(".")[1]
            links = job_element.find_all("a")
            for link in links:
                link_url = link["href"]

            title_element_clean = title_element.text.strip()
            link_url_clean = "https://pubmed.ncbi.nlm.nih.gov" + link_url

            print(title_element_clean)
            print()

            df2 = pd.DataFrame(
                [
                    [
                        title_element_clean,
                        authors,
                        year,
                        link_url_clean,
                        cit_element,
                        description,
                    ]
                ],
                columns=[
                    "Title",
                    "Authors",
                    "Year",
                    "Links",
                    "References",
                    "Description",
                ],
            )
            df = pd.concat([df, df2], ignore_index=True)

            with open("scrapped_pubmed.csv", "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        title_element_clean,
                        authors,
                        year,
                        link_url_clean,
                        cit_element,
                        description,
                    ]
                )

        # wait()

    except AttributeError:

        print("Opss! ReCaptcha is probably preventing the code from running.")
        print("Please consider running in another time.\n")
        exit()

    df.index += 1
    df.to_csv("scrapped_pubmed.csv")
    outfile.close()


# ===== CODE FOR GOOGLE SCHOLAR =====

elif search_from == "Google Scholar":

    try:

        # SETTING UP THE CSV FILE

        outfile = open("scrapped_gscholar.csv", "w", newline="", encoding="utf-8")
        writer = csv.writer(outfile)
        df = pd.DataFrame(columns=["Title", "Links", "References"])

        # SETTING & GETTING PAGE NUMBER

        page_num = 0
        URL_edit = str(URL_ori + "&start=" + str(page_num))

        page = requests.get(URL_edit, headers=headers, timeout=None)
        soup = BeautifulSoup(page.content, "html.parser")
        wait()

        search_results = soup.find_all("div", class_="gs_ab_mdw")[1].text

        if "About" in search_results:
            search_results_split = search_results.split("results")[0].split("About")[1]
        elif "results" in search_results:
            search_results_split = search_results.split("results")[0]
        else:
            search_results_split = search_results.split("result")[0]

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

    # EXTRACTING INFORMATION

    for i in range(page_total_num):

        # SETTING UP URL SECOND TIME

        page_num_up = 98 + i
        print(f"Going to page {page_num_up}.\n")
        URL_edit = str(URL_ori + "&start=" + str(page_num_up) + "0")
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

        results = soup.find("div", id="gs_res_ccl_mid")
        paper_doc = BeautifulSoup(response.text, "html.parser")

        # EXTRACTING INFORMATION

        try:

            job_elements = results.find_all("div", class_="gs_ri")
            for job_element in job_elements:
                try:
                    ref_element = job_element.find("div", class_="gs_a").text
                    links = job_element.find("a")
                    link_url = links["href"]
                    # author_tag = paper_doc.find_all("div", {"class": "gs_a"})
                    abstract = job_element.find("div", class_="gs_rs").text
                    title_element = job_element.find("h3", class_="gs_rt")
                    title_element = links.text.strip()
                    # data_source = job_element.find("div", class_="gs_or_ggsm").text
                    publisher = job_element.find("div", class_="gs_a").text.split(
                        " - "
                    )[1]
                    year_and_tag = (
                        job_element.find("div", class_="gs_a")
                        .text.split(" - ")[0]
                        .split("-")[1]
                    )
                    year = year_and_tag.split(",")[1]
                    tag = year_and_tag.split(",")[0]
                    cites = (
                        job_element.find("div", class_="gs_fl")
                        .text.split("Cited by ")[1]
                        .split(" ")[0]
                    )
                except Exception as e:
                    print(e)
                    continue
                print(title_element)

                df2 = pd.DataFrame(
                    [
                        [
                            title_element,
                            cites,
                            year,
                            ref_element,
                            publisher,
                            tag,
                            link_url,
                            abstract,
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
                headers = [
                    "Title",
                    "Cites",
                    "Year",
                    "Reference",
                    "Publisher",
                    "Tag",
                    "Link",
                    "Description",
                ]

                with open(
                    "scrapped_gscholar_try.csv", "a", newline="", encoding="utf-8"
                ) as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [
                            title_element,
                            cites,
                            year,
                            ref_element,
                            publisher,
                            tag,
                            link_url,
                            abstract,
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
