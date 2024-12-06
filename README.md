# Movie Data Scraper

## Overview

This Python script scrapes movie data from IMDb for a specified date range. It utilizes Selenium for web automation and asyncio for asynchronous operations, allowing for efficient data collection. The script extracts various details about movies, including title, year, genres, director, cast, reviews, and box office information.

## Features

- Scrapes movie data from IMDb based on specified release dates.
- Extracts detailed information such as:
  - Title
  - Year
  - Genres
  - Director
  - Writer
  - Cast
  - Metascore
  - Synopsis
  - Runtime
  - IMDb Score
  - User and Critic Reviews
  - Box Office Data
  - Keywords
- Saves the collected data into a CSV file asynchronously.

## Requirements

- Python 3.x
- Required Python packages:
  - `pandas`
  - `aiofiles`
  - `selenium`
  - `asyncio`
  - `re`
  - `logging`

You can install the required packages using pip:

```bash
pip install pandas aiofiles selenium
```

## Setup

1. **Download ChromeDriver**: Ensure you have the ChromeDriver executable (`chromedriver.exe`) in the same directory as the script. You can download it from [ChromeDriver's official site](https://sites.google.com/chromium.org/driver/).

2. **Set Chrome Path**: Update the `chrome_browser_path` variable in the `initialize_webdriver` function to point to your Chrome installation.

3. **Create Data Directory**: The script saves the output CSV file in a `data` directory. Ensure this directory exists or the script will create it automatically.

## Usage

To run the script, execute the following command in your terminal:

```bash
python script.py
```

The script will navigate to IMDb, scrape the movie data for the specified date range, and save the results in `data/movies_complete_data.csv`.

## Logging

The script logs its activities to a file named `scraping.log`. This log file will contain information about the scraping process, including any errors encountered.

## Notes

- Ensure that you have the necessary permissions to scrape data from IMDb and comply with their terms of service.
- The script is designed to run in headless mode by default. You can modify the options in the `initialize_webdriver` function if you want to see the browser actions.

## Acknowledgments

- Thanks to the developers of Selenium and the contributors of the libraries used in this project.
