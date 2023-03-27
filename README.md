Crawler project README.md

Xinchang Meng: Finished Start crawling function. The function implements the basic web crawler by parsing through the HTML content of the current URL and searching for more URLs and/or secret flags until all secret flags are found for the user. The function also accounts for and appropriately handles different errors received when parsing through pages, such as redirect pages, response codes in the 4xx (client errors) and 5xx (server errors) ranges, and the cases where the response code is in the 2xx (success) range bu using proper helper functions.
