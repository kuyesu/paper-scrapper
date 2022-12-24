import pandas as pd
from sys import exit
from bs4 import BeautifulSoup
import time
import random
import requests
import csv

# ===== DEFINE FUNCTIONS =====

search_from, URL_edit = "", ""


def wait():
    print("Waiting for a few secs...")
    time.sleep(random.randrange(1, 6))
    print("Waiting done. Continuing...\n")


# ===== GETTING AND SETTING THE URL =====

URL_input = input("Please paste search URL and press Enter:")
URL_ori = URL_input
headers = requests.utils.default_headers()
headers.update(
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    }
)


# ===== MAIN FRAMEWORK =====

# ===== CODE FOR PUBMED =====


try:
    # SETTING UP THE CSV FILE
    outfile = open("scrapped_pubmed.csv", "w", newline="", encoding="utf-8")
    writer = csv.writer(outfile)
    df = pd.DataFrame(
        columns=["Title", "Authors", "Year", "Links", "References", "Description"]
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

    for i in range(page_total_num):
        page_num_up = page_num + i
        print("Page number: ", page_num_up)
        URL_edit = URL_ori + "&page=" + str(page_num_up) + "&size=" + str(page_view)
        page = requests.get(URL_edit, headers=headers, timeout=None)

        # print("page status: ", page)
        soup = BeautifulSoup(page.content, "html.parser")
        # print(soup.prettify())
        wait()
        results = soup.find("section", class_="search-results-list")
        # print(results.prettify())

        try:
            # EXTRACTING INFORMATION

            job_elements = results.find_all("article", class_="full-docsum")
            print("Number of results: " + "\n " + job_elements)

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

                with open(
                    "scrapped_pubmed.csv", "a", newline="", encoding="utf-8"
                ) as f:
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
            df.index += 1
            df.to_csv("scrapped_pubmed.csv")
            outfile.close()

        except Exception as e:
            print("Opss! ReCaptcha is probably preventing the code from running.")
            print("Please consider running in another time.\n")
            # exit()
            wait()

except Exception as e:
    print("Opss! ReCaptcha is probably preventing the code from running.")
    print("Please consider running in another time.\n")
    # exit()
    wait()
