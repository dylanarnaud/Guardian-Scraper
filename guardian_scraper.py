# Libraries
import re
import string
import pandas as pd
import requests
import sqlite3
import logging
from bs4 import BeautifulSoup as bs
from typing import List
from datetime import datetime

# Set up the logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

class GuardianScraper:
    def __init__(self):
        self.data = None

    def __generate_guardian_world_urls(self, end_page: int) -> list:
        """
        Generates Guardian "world" section URLs up to a certain page number.
        
        Parameters:
        - end_page (int): The last page number up to which URLs should be generated.
        
        Returns:
        - list: A list of URLs for the Guardian "world" section up to the specified page number.
        """
        
        base_url = "https://www.theguardian.com/world?page="
        
        # Generate URLs for each page number from 1 to end_page
        urls = [base_url + str(page) for page in range(1, end_page + 1)]
        
        return urls

    def __extract_guardian_world_links(self, url: str = "https://www.theguardian.com/world?page=1") -> list:
        """
        Extracts article links from the provided Guardian "world" page URL.
        
        Parameters:
        - url (str): The URL of the Guardian "world" page.
        
        Returns:
        - list: A list of URLs extracted from the page. Returns an empty list if no URLs are found.
        """
        
        # Send a GET request to retrieve the page content
        response = requests.get(url)
        
        # Ensure a successful response
        if response.status_code != 200:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return []

        # Parse the content using BeautifulSoup
        soup = bs(response.content, 'html.parser')
        
        # Extract URLs from elements with class 'fc-item__content'
        urls = [link.a['href'] for link in soup.find_all('div', class_='fc-item__content') if link.a]
        
        return urls
    
    def __collect_urls_until_target(self, target_url: str = None, end_page: int = 1) -> list:
        """
        Extracts article URLs from the Guardian "world" section up to a certain page number 
        or until a specific URL is found.
        """
        # Generate Guardian "world" section URLs up to the specified page number
        page_urls = self.__generate_guardian_world_urls(end_page)

        all_article_urls = []
        for index, page_url in enumerate(page_urls, 1):  # Start enumeration from 1 for human-readable page numbers
            logging.info(f"Scraping links from page {index} out of {end_page}.")

            # Extract article URLs from the current page
            article_urls = self.__extract_guardian_world_links(page_url)

            # Provide feedback on how many article links were scraped from the current page
            #print(f"Retrieved {len(article_urls)} links from page {index}.")

            if target_url and target_url in article_urls:
                # If target_url is found among the article URLs, 
                # append all the URLs up to (but not including) the target_url, 
                # then break out of the loop.
                all_article_urls.extend(article_urls[:article_urls.index(target_url)])
                break
            else:
                all_article_urls.extend(article_urls)

        return all_article_urls

    def __filter_urls_by_category(self, urls: list, category: str = 'world', filter_by_date: bool = False) -> list:
        """
        Filters URLs to retain only those that belong to a specific category. Optionally filters URLs to retain only those 
        that contain a year after the category.

        Parameters:
        - urls (list): A list of URLs to filter.
        - category (str): The desired category to filter by. Default is 'world'.
        - filter_by_date (bool): A flag to determine whether to filter URLs with a year after the category. Default is False.

        Returns:
        - list: A list of filtered URLs.
        """
        
        # First filter by category
        filtered_urls = [url for url in urls if f"/{category}/" in url]
        
        # If filter_by_date is True, further filter the URLs to match the pattern:
        # `https://www.theguardian.com/{category}/{year}/{month}/{day}/...`.
        # Where:
        # - {year} is a 4-digit representation of the year.
        # - {month} is the full lowercase representation of the month (e.g., 'january', 'february').
        # - {day} is a 1 or 2-digit representation of the day of the month (e.g., '1', '31').
        if filter_by_date:
            pattern = re.compile(rf'/{category}/\d{{4}}/[a-z]+/\d{{1,2}}/')
            filtered_urls = [url for url in filtered_urls if pattern.search(url)]
                
        return filtered_urls
    
    def __get_category(self, url: str) -> str:
        """
        Extracts the main category from a given The Guardian URL using string manipulation.
        
        Parameters:
        - url (str): The URL from which the main category is to be extracted.
        
        Returns:
        - str: The extracted main category. Returns None if the URL is not in the expected format or category is not found.
        """
        
        # Strip the leading "https://www.theguardian.com/" from the URL
        stripped_url = url.replace("https://www.theguardian.com/", "")
        
        # Split the remaining string by '/'
        segments = stripped_url.split('/')
        
        # The first segment should be the main category
        if segments:
            return segments[0]
        
        # Return None if category can't be extracted
        return None

    def __get_article_date(self, url: str) -> str:
        """
        Extracts the article's date from a given The Guardian URL using regex.
        
        Parameters:
        - url (str): The URL from which the article's date is to be extracted.
        
        Returns:
        - datetime.date: The extracted date as a date object. 
                        Returns None if the URL is not in the expected format or date is not found.
        """
        
        # Use regex to extract the date in the format YYYY/MON/DD from the URL
        match = re.search(r'/(\d{4}/[a-z]+/\d{1,2})/', url)
        
        # If a match is found, transform the matched string to a date object
        if match:
            year, month_str, day = match.group(1).split('/')
            month = datetime.strptime(month_str, '%b').month
            # Convert the date object to a string
            return datetime(int(year), month, int(day)).date().isoformat()
        
        # Return None if date can't be extracted
        return None
    
    def __get_author(self, url: str) -> str:
        """
        Fetches and extracts the author's name from a given URL.
        
        Parameters:
        - url (str): The URL of the web page to extract the author's name from.
        
        Returns:
        - str: The extracted author's name from the target element on the webpage. 
            Returns None if the page retrieval was unsuccessful or if the target element was not found.
        """
        
        # Send a GET request to the provided URL to retrieve the page content
        article = requests.get(url)
        
        # Check if the GET request was successful (status code 200)
        # If not, the function will return None indicating the article couldn't be fetched.
        if article.status_code != 200:
            return None

        # Parse the page content using BeautifulSoup to create a navigable structure
        soup = bs(article.content, 'html.parser')
        
        # Attempt to find the target element based on its attributes
        target_element = soup.find('a', attrs={'rel': 'author', 'data-link-name': 'auto tag link'})
        
        # Check if the target element was found:
        # If found, return its text content.
        # If not found, return None.
        return target_element.text if target_element else None
    
    def __get_headline(self, url: str) -> str:
        """
        Fetches and extracts the headline of an article from a given URL.
        
        Parameters:
        - url (str): The URL of the web page to extract the headline from.
        
        Returns:
        - str: The extracted headline from the target element on the webpage. 
            Returns None if the page retrieval was unsuccessful or if the target element was not found.
        """
        
        # Send a GET request to the provided URL to retrieve the page content
        article = requests.get(url)
        
        # Check if the GET request was successful (status code 200)
        # If not, the function will return None indicating the article couldn't be fetched.
        if article.status_code != 200:
            return None

        # Parse the page content using BeautifulSoup to create a navigable structure
        soup = bs(article.content, 'html.parser')
        
        # Attempt to find the target element based on the data attribute and then locate the <h1> tag
        headline_div = soup.find('div', attrs={'data-gu-name': 'headline'})
        if headline_div:
            headline = headline_div.find('h1')
            if headline:
                return headline.text

        return None
    
    def __get_text(self, url: str) -> str:
        """
        Fetches and extracts the main text content of an article from a given URL.
        
        Parameters:
        - url (str): The URL of the web page to extract the text content from.
        
        Returns:
        - str: The extracted text content from the target element on the webpage. 
            Returns None if the page retrieval was unsuccessful or if the target element was not found.
        """
        
        # Send a GET request to the provided URL to retrieve the page content
        article = requests.get(url)
        
        # Check if the GET request was successful (status code 200)
        # If not, the function will return None indicating the article couldn't be fetched.
        if article.status_code != 200:
            return None

        # Parse the page content using BeautifulSoup to create a navigable structure
        soup = bs(article.content, 'html.parser')
        
        # Attempt to find the target element based on the data attribute and then extract its text
        text_div = soup.find('div', attrs={'data-gu-name': 'body'})
        if text_div:
            return text_div.text.strip()

        return None
    
    def __fetch_world_articles_details(self, end_page: int = 1) -> dict:
        """
        Fetches details (category, headline, author, and text) for articles from the 'world' category up to a specified page number.

        Parameters:
        - end_page (int): The last page number up to which articles should be fetched. Default is 1.

        Returns:
        - dict: A dictionary with URLs as keys and their details as values.
        """
        
        logging.info(f"Starting the scraping process for up to {end_page} pages.")
        
        # Fetching the list of all article URLs
        all_article_urls = self.__collect_urls_until_target(end_page=end_page)
        
        # Filter all articles to retain only the ones from the 'world' category
        world_article_urls = self.__filter_urls_by_category(urls=all_article_urls, category="world", filter_by_date=True)
        
        # Logging the total number of articles to be processed
        total_articles = len(world_article_urls)
        logging.info(f"Total articles to process from 'world' category: {total_articles}")

        # Initialize the result dictionary
        result = {}

        for index, url in enumerate(world_article_urls, start=1):
            # Log the scraping progress
            logging.info(f"Scraping article {index} out of {total_articles}: {url}")
            
            # Get the details for each article
            category = self.__get_category(url)
            article_date = self.__get_article_date(url)
            author = self.__get_author(url)
            headline = self.__get_headline(url)
            text = self.__get_text(url)

            # Add the details to the result dictionary
            result[url] = {
                "category": category,
                "date": article_date,
                "headline": headline,
                "author": author,
                "text": text
            }

        logging.info(f"Finished scraping {total_articles} articles from 'world' category.")
        
        return result

    def scrape_data(self, page_count = 1):
        # Fetch the article details
        articles_details = self.__fetch_world_articles_details(end_page = page_count)

        # Convert the dictionary to a DataFrame
        self.data = pd.DataFrame.from_dict(articles_details, orient='index')