# 🌟 Guardian Scraper App 🌟

Guardian Scraper App is your go-to Python solution for fetching, processing, and managing articles from The Guardian's online platform.

## 📌 Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Deployment Instructions](#deployment-instructions)
- [Configuration (Environment Variables)](#configuration-environment-variables)
- [API Endpoints Guide](#api-endpoints-guide)
- [Limitations](#limitations)
- [Suggestions for Improvement](#suggestions-for-improvement)

<a id="features"></a>
## 💡 Features
- **Swift Web Scraping** with Beautifulsoup4.
- **Data Aggregation** using the renowned Pandas library.
- **Persistent Storage** with SQLite3.
- **API Accessibility** with Flask API for developers, journalists, or analysts.

<a id="prerequisites"></a>
## 🖥️ Prerequisites

- Docker installed on your system. If not, [download and install Docker](https://www.docker.com/products/docker-desktop/).

<a id="deployment-instructions"></a>
## 🚀 Deployment Instructions

Clone the repository:
```bash
git clone https://github.com/dylanarnaud/Guardian-Scraper.git
cd <repository-folder>
```

Build the Docker image:
```bash
docker build --pull --rm -f "Dockerfile" -t guardianscraper:latest --no-cache "."
```

Run the Docker container:
```bash
docker run -d -p 5000:5000 --name guardianscraper-container guardianscraper:latest
```

Note: By default, the app inside the container will run on port 5000, mapped to your machine's port 5000. Adjust the port if necessary.

<a id="configuration-environment-variables"></a>
## 🔧 Configuration (Environment Variables)
Fine-tune the behavior of the app using the following environment variables:

- **`NUM_SCRAPER_PAGES_INITIAL`:** Set the initial number of pages to scrape (default: 100).
- **`NUM_SCRAPER_PAGES`:** Specify the number of pages to scrape (default: 1).
- **`MINUTES_BETWEEN_RUNS`:** Define the interval between scraper runs (default: 60 minutes).
- **`FLASK_HOST`:** Determine the host IP for the Flask application.
    - Use `FLASK_HOST=127.0.0.1` to make the Flask app only accessible internally (i.e., from the machine where the container is running). This is a secure setting for testing or local development.
    - Use `FLASK_HOST=0.0.0.0` to make the Flask app accessible externally, meaning it can be reached from any device on the network. This is useful when you want to make your application available to the world but comes with potential security considerations.

For example:
1. Running the scraper for local development:
This command will set the app to only be accessible from the local machine. It also adjusts the scraping settings for testing purposes.
    ```bash
    docker run -p 5000:5000 -e FLASK_HOST=127.0.0.1 -e NUM_SCRAPER_PAGES_INITIAL=10 -e NUM_SCRAPER_PAGES=1 -e MINUTES_BETWEEN_RUNS=10 guardianscraper
    ```

2. Running the scraper for external accessibility:
This command will make your app available to any device on your network or even the internet if your server has a public IP. It also sets default scraping parameters.
    ```bash
    docker run -p 5000:5000 -e FLASK_HOST=0.0.0.0 -e NUM_SCRAPER_PAGES_INITIAL=100 -e NUM_SCRAPER_PAGES=1 -e MINUTES_BETWEEN_RUNS=60 guardianscraper
    ```

3. Running the scraper with custom scraping parameters:
Suppose you want to scrape 5 initial pages, then 3 pages on each subsequent run, and run the scraper every 30 minutes. At the same time, you want the app to be externally accessible. The command would look like:
    ```bash
    docker run -p 5000:5000 -e FLASK_HOST=0.0.0.0 -e NUM_SCRAPER_PAGES_INITIAL=5 -e NUM_SCRAPER_PAGES=3 -e MINUTES_BETWEEN_RUNS=30 guardianscraper
    ```

Remember, adjusting the `FLASK_HOST` value affects the accessibility of your application, so choose the setting that aligns with your needs and security considerations.

<a id="api-endpoints-guide"></a>
## 🌐 API Endpoint Guide

1. Fetch Articles with Pagination:
- **Endpoint**: `/items`
- **Description**: Retrieve a list of articles.
- **Usage**: By default, the first page with the initial 10 articles is returned. For custom results, modify the request parameters.
- **Curl Command**:
    ```bash
    curl http://localhost:5000/items?page=2&per_page=5
    ```

2. Today's Articles:
- **Endpoint**: `/today`
- **Description**: Retrieve articles published today.
- **Usage**: If multiple articles are available, the first 10 are shown by default. Adjust the request parameters for customized results.
- **Curl Command**:
    ```bash
    curl http://localhost:5000/today?page=2&per_page=5
    ```

3. Fetch the Latest Article:
- **Endpoint**: `/last`
- **Description**: Retrieve the most recent article from the database.
- **Usage**: A simple GET request fetches the latest article.
- **Curl Command**:
    ```bash
    curl http://localhost:5000/last
    ```

4. Discover Prolific Authors:
- **Endpoint**: `/top-authors`
- **Description**: Rank and retrieve authors based on their publication frequency.
- **Usage**: A straightforward GET request presents authors with the most articles.
- **Curl Command**:
    ```bash
    curl http://localhost:5000/top-authors
    ```

5. Secure Shutdown:
- **Endpoint**: `/shutdown`
- **Description**: Allows for a safe application termination.
- **Usage**: Make a POST request with the required secret key for authentication. For enhanced security in a production setup, it's advisable to use a more advanced authentication mechanism.
- **Curl Command** (POST request example with a placeholder for a secret key):
    ```bash
    curl -X POST -H "Authorization: Bearer [YOUR_SECRET_KEY]" http://localhost:5000/shutdown
    ```
- **Note**: Unauthorized requests will be met with a 401 response.

<a id="limitations"></a>
## ⚠️ Limitations
- Dependence on Page Structure: The scraper relies on specific HTML tags, so if The Guardian's website structure changes, the scraper may break.
- Rate Limiting: Frequent requests might get IP-blocked by The Guardian's servers.
- No Parallelization: The script processes pages sequentially, which can be slow for large numbers of pages.

<a id="suggestions-for-improvement"></a>
## 🌱 Suggestions for Improvement
- Use another Framework: Tools like Scrapy can provide a more robust and efficient scraping process with built-in functionalities.
- Parallel Processing: Implement multi-threading or multi-processing to scrape multiple pages simultaneously.
- Distributed Scraping: Using proxies or tools like Scrapy Cloud to distribute the scraping tasks to avoid rate limits and increase efficiency.