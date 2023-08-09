# Guardian Scraper App

## Table of Contents
- [Overview](#overview)
- [Deployment Instructions](#deployment-instructions)
- [Configuration](#configuration)
- [Execution](#execution)
- [Functionality Guide](#functionality-guide)
- [Limitations](#limitations)
- [Improvements](#improvements)
- [License](#license)

## Overview

The Guardian Scraper App is a versatile Python application designed to fetch, process, and manage articles from The Guardian's online platform. Here's what it offers:

- **Web Scraping with Beautifulsoup4:** Parse The Guardian's structure swiftly and accurately. The scraper is designed to be robust and resilient to changes in the website's structure.
- **Data Aggregation using Pandas:** Aggregate data leveraging the pandas library.
- **Persistent Storage with SQLite3:** Store data in an SQLite3 database for fast and reliable retrieval.
- **API Accessibility through Flask API:** Make data accessible for developers, journalists, or analysts.

Whether you're tracking evolving news, conducting deep data analyses, or integrating content into other platforms, the Guardian Scraper App is up to the task.

## Deployment Instructions:
Prerequisites: Ensure Python 3.10.0 or higher is installed. Check using: python **--version** or **python3 --version**.

Install pipenv:
```bash
pip install pipenv
```

Install project dependencies:
```bash
pipenv install
```

Activate the virtual environment:
```bash
pipenv shell
```

## Configuration
To tailor the app to your needs, open `app.py` in a text editor. Adjust constants under the **'Constants'** section. The default setup scraps the first page every hour. Modify **'MINUTES_BETWEEN_RUNS'** and **'NUM_SCRAPER_PAGES'** constants to adjust scraping frequency and depth, respectively.

## Execution
After setting up dependencies and configuration, run the scraper using the command:
```bash
python app.py
```

You can end the execution by pressing **CTRL + C**.

## Functionality Guide

The Guardian Flask API facilitates efficient article management and retrieval. Here's a breakdown of its operations:

### Data Retrieval:
- **Fetch Articles with Pagination:**
    - Endpoint: **/items**
    - Description: To retrieve a list of articles.
    - Usage: By default, the first page with the initial 10 articles is returned. For custom results, modify the request parameters.
    - Example: /items?page=2&per_page=5

- **Today's Articles:**
    - Endpoint: **/today**
    - Description: Retrieve articles published today.
    - Usage: If multiple articles are available, the first 10 are shown by default. For customized results, adjust the request parameters.
    - Example: /today?page=2&per_page=5

- **Fetch the Latest Article:**
    - Endpoint: **/last**
    - Description: Ensures the most recent article from the database is retrieved.
    - Usage: A simple GET request will fetch the latest article.

- **Discover Prolific Authors:**
    - Endpoint: **/top-authors**
    - Description: Rank and retrieve authors based on their publication frequency.
    - Usage: A straightforward GET request presents authors with the most articles.

### Application Shutdown:
- **Secure Shutdown:**
    - Endpoint: **/shutdown**
    - Description: Allows for a safe application termination.
    - Usage: Make a POST request with the required secret key for authentication. - For security in a production setup, it's advised to utilize a more advanced authentication mechanism.
    - Note: Unauthorized requests will be met with a 401 response.

## Limitations:
- Dependence on Page Structure: The scraper relies on specific HTML tags, so if The Guardian's website structure changes, the scraper may break.
- Rate Limiting: Frequent requests might get IP-blocked by The Guardian's servers.
- No Parallelization: The script processes pages sequentially, which can be slow for large numbers of pages.

## Improvements:
- Use another Framework: Tools like Scrapy can provide a more robust and efficient scraping process with built-in functionalities.
- Parallel Processing: Implement multi-threading or multi-processing to scrape multiple pages simultaneously.
- Distributed Scraping: Using proxies or tools like Scrapy Cloud to distribute the scraping tasks to avoid rate limits and increase efficiency.

## License

Copyright (c) 2023 DYLAN ARNAUD

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.