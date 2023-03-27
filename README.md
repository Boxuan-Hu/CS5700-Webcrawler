Crawler project README.md
Xinchang Meng: Finished Start crawling function
redirect_page(msg) function that takes in a message received from the web server and parses it to extract the redirected page's URL if the response status code is a 3xx (redirect) status code. 
The function returns the URL of the redirected page.

get_res(msg) function that takes in a message received from the web server and extracts the response code from it. 
It then returns the response code as an integer.

start_crawling(msg, sock, host, cookie3, cookie4) function that takes in a message received from the web server, a socket connection, a host, and two cookies. 
The function implements the basic web crawler by parsing through the HTML content of the current URL and searching for more URLs and/or secret flags until all secret flags are found for the user. 
The function also accounts for and appropriately handles different errors received when parsing through pages, such as redirect pages, response codes in the 4xx (client errors) and 5xx (server errors) ranges, and the cases where the response code is in the 2xx (success) range. 
The FakebookHTMLParser() is used to parse through the HTML content of the web page. The function adds the newly found URLs to a not_crawled_page queue and pops the first URL from the queue to crawl it. If a URL is already crawled, it is added to the crawled_page set to prevent redundant crawling. 
If the response code is in the 2xx range, the parser is used to parse the HTML content and search for secret flags. If the response code is in the 3xx range, the redirect_page() function is called to get the URL of the redirected page, and the URL is added to the not_crawled_page queue. 
If the response code is in the 4xx range, the current URL is added to the crawled_page set, and the function continues to the next URL in the not_crawled_page queue. If the response code is in the 5xx range, the current URL is added back to the not_crawled_page queue, and the function continues to the next URL in the queue. 
The function stops crawling if all five secret flags are found.