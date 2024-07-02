"""

Author: Fer Aguirre
Date: 2024-07-01

This script is designed to perform asynchronous scraping of Pubmed, 
a freely accessible database of academic research papers. It extracts 
data based on a list of URLs provided in a CSV file and stores the 
information in a DataFrame. The data is then exported to a CSV file 
for subsequent analysis and processing. The asynchronous nature of 
the script allows for efficient and simultaneous data retrieval. 
The script uses the aiohttp library for making HTTP requests, 
BeautifulSoup for parsing HTML content, and asyncio for managing 
asynchronous tasks. It also uses pandas for data manipulation and storage. 


The script contains a Scraper class with the following methods:

    load_data: Loads the URLs from the CSV file into a pandas DataFrame.
    get_html_content: Fetches the HTML content of a given URL.
    scrape_data: Scrapes the data from a given URL and returns a dictionary of the scraped data.
    scrape_all: Scrapes the data from all URLs in the DataFrame.
    format_time: Formats the elapsed time into a readable string.
    print_results: Prints the results of the scraping process.
    save_results: Saves the results to a CSV file.

The script also contains a main function that creates an instance of the 
Scraper class, loads the data, scrapes the data, saves the results, and 
prints the results. The script accepts the following command-line arguments:

    --input_file: Path to the input CSV file containing URLs to be scraped.
    --delay: Delay between each request in seconds. This is to prevent overloading the server with requests. Default is 1 second.
    --max_requests: Maximum number of concurrent requests that can be made. This is to prevent overloading the server with too many requests at once. Default is 5.
    --output_file: Path to the output CSV file where the scraped data will be saved.

Requires:

    pandas
    datetime
    beautifulsoup4
    aiohttp
    asyncio
    argparse
    nest_asyncio 

"""

import argparse
import pandas as pd
import aiohttp
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup
import nest_asyncio

nest_asyncio.apply()

class Scraper:
    """
    A class used to scrape data from URLs.

    Attributes
    ----------
    file_path : str
        Path to the CSV file containing URLs.
    delay : int
        Delay between requests in seconds (default 1).
    max_requests : int
        Maximum number of concurrent requests (default 5).
    """

    def __init__(self, file_path, delay=1, max_requests=5):
        self.file_path = file_path
        self.df = None
        self.start_time = datetime.now()
        self.delay = delay
        self.semaphore = asyncio.Semaphore(max_requests)

    def load_data(self):
        """Loads the URLs from the CSV file into a pandas DataFrame."""
        self.df = pd.read_csv(self.file_path)
        self.df = self.df[["url"]]

    async def get_html_content(self, url):
        """Fetches the HTML content of a given URL."""
        async with self.semaphore:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        await asyncio.sleep(self.delay)
                        return await response.text()
            except asyncio.TimeoutError:
                print(f"TimeoutError occurred while fetching {url}")
                return None

    async def scrape_data(self, url):
        """Scrapes the data from a given URL and returns a dictionary of the scraped data."""
        html_content = await self.get_html_content(url)
        if html_content is None:
            return None
        soup = BeautifulSoup(html_content, "html.parser")

        elements = {
            "title": "header#heading.heading div#full-view-heading.full-view h1.heading-title",
            "publication_type": "header#heading.heading div#short-view-heading.short-view div.publication-type",
            "journal": "header#heading.heading div#full-view-heading.full-view div.article-citation div.article-source div.journal-actions.dropdown-block button#full-view-journal-trigger.journal-actions-trigger.trigger",
            "coi": "div#conflict-of-interest.conflict-of-interest div.statement p",
            "grants": "div#grants.grants",
            "authors": "header#heading.heading div#full-view-heading.full-view div.inline-authors div.authors div.authors-list",
            "abstracts": "div#abstract.abstract div#eng-abstract.abstract-content.selected",
            "pmid": "header#heading.heading div#full-view-heading.full-view ul#full-view-identifiers.identifiers li span.identifier.pubmed strong.current-id",
            "pmcid": "header#heading.heading div#full-view-heading.full-view ul#full-view-identifiers.identifiers li span.identifier.pmc a.id-link",
            "doi": "header#heading.heading div#full-view-heading.full-view ul#full-view-identifiers.identifiers li span.identifier.doi a.id-link",
            "citation": "header#heading.heading div#full-view-heading.full-view div.article-citation div.article-source span.cit",
            "erratum": "main#article-details.article-details div#linked-correction-forward.linked-articles",
        }

        texts = {}
        for key, value in elements.items():
            element = soup.select(value)
            texts[key] = " ".join(e.text.strip() for e in element) if element else pd.NA

        return texts

    async def scrape_all(self):
        """Scrapes the data from all URLs in the DataFrame."""
        tasks = [self.scrape_data(url) for url in self.df["url"]]
        results = await asyncio.gather(*tasks)
        scraped_df = pd.DataFrame(results)
        self.df = pd.concat([self.df, scraped_df], axis=1)

    def format_time(self, elapsed_time):
        """Formats the elapsed time into a readable string."""
        if elapsed_time < 60:
            return f"{elapsed_time} seconds"
        elif elapsed_time < 3600:
            return f"{elapsed_time / 60} minutes"
        else:
            return f"{elapsed_time / 3600} hours"

    def print_results(self):
        """Prints the results of the scraping process."""
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        formatted_time = self.format_time(elapsed_time)
        print(f"It took {formatted_time} to find {len(self.df)} articles")
        print('Preview of scraped data:\n', self.df.head(5))
        return self.df

    def save_results(self, output_file):
        """Saves the results to a CSV file."""
        self.df.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")


async def main(file_path, delay, max_requests, output_file):
    """Main function to run the scraper."""
    scraper = Scraper(file_path, delay, max_requests)
    scraper.load_data()
    await scraper.scrape_all()
    scraper.save_results(output_file)
    scraper.print_results()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This script scrapes data from a list of PubMed URLs provided in a CSV file and saves the scraped data into another CSV file.')
    
    parser.add_argument('--input_file', type=str, required=True, 
                        help='Path to the input CSV file containing URLs to be scraped.')
    
    parser.add_argument('--delay', type=int, default=1, 
                        help='Delay between each request in seconds. This is to prevent overloading the server with requests. Default is 1 second.')
    
    parser.add_argument('--max_requests', type=int, default=5, 
                        help='Maximum number of concurrent requests that can be made. This is to prevent overloading the server with too many requests at once. Default is 5.')
    
    parser.add_argument('--output_file', type=str, required=True, 
                        help='Path to the output CSV file where the scraped data will be saved.')
    
    args = parser.parse_args()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main(args.input_file, args.delay, args.max_requests, args.output_file))
    finally:
        loop.close()

