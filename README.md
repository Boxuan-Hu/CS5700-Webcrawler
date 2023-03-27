## Prerequisites

This project requires python3 environment.

## How to run the code

```
python3 webcrawler.py <username> <password>
```

## Output

Five secret flags like this:

```
cdbfb5f485a6d01984e95e78b60850f8bf5ab33146822a78e21b1991d704f4bc
ee7ff918d1392c6807c8ff6aaaa0f88b95324664da4db8d003e3b589db3f399f
bb4495dce0ce3d52e4f3a8f9e6e344465707850e5e252f41e464d6133aceac63
dea02195ff21e8426c4c33ca19fa240a1132e6c49bb15ce8fe600a63ec503737
e5f679c2229e358442e89f30776327766b91d0f69f16529f15381b057d34aae3
```

## High-Level Approach

The program has to be run by inputing username and password. First, the program creates a TLS socket and establishes the TCP connection with the “fakebook” website. The program sends an HTTP GET request for the login page, receives the HTTP response from the server, and extracts the csrf cookies and csrf middleware tokens from it. Then, the login body is created by using username, password, and csrfmiddleware token, and the login header is created using csrf cookie. The program then sends an HTTP POST request containing login body and header to the server. The server responds with an HTTP response, indicating whether the login was successful or not. If successful, the program extracts the session cookies and uses them to navigate to the home page.

Next, the program then starts crawling the website by sending HTTP GET requests to URLs and parsing the HTML content of each page. As the program crawls the website, it searches for secret flags embedded within the HTML content of each page using the FakebookHTMLParser(). If the program encounters a URL that requires authentication, it will repeat the authentication process as described above. If the program encounters a URL that is a redirect, it will follow the redirect and continue crawling from the new URL. If the program encounters a URL that returns a 4xx status code, it will skip the URL and continue crawling. If the program encounters a URL that returns a 5xx status code, it will add the URL back to the queue and continue crawling. Once the program has found all five secret flags, it will stop crawling and print out the flags.

## Work Breakdown

### Xinchang Meng

Finished Start crawling function. The function implements the basic web crawler by parsing through the HTML content of the current URL and searching for more URLs and/or secret flags until all secret flags are found for the user. The function also accounts for and appropriately handles different errors received when parsing through pages, such as redirect pages, response codes in the 4xx (client errors) and 5xx (server errors) ranges, and the cases where the response code is in the 2xx (success) range by using proper helper functions.

### Boxuan Hu

I finished all the codes before starting crawling, including parsing username and password, getting the root page and login page, receiving messages, extracting session cookie, csrf cookie, csrf middleware token and sending post request using the credentials extracted before.

### Kan Zhou

Finished the constructor of FakebookHTMLParser, which extends the HTMLParser class. I override three methods in FakebookHTMLParser class.
Override three methods: handle_starttag, handle_endtag, handle_data

## Testing & Challenges

### Xinchang Meng

Handling authentication errors: The code assumes that the authentication process will always succeed. However, if the server changes the authentication mechanism or requires additional parameters, the code may not be able to log in properly. 2.Parsing complex HTML: The FakebookHTMLParser class assumes that the HTML content it receives is well-formed and structured. If the HTML is malformed or contains unexpected elements, the parser may not work as expected.

I did test manually, involved navigating the website manually to verify that the crawler is properly following links, extracting content, and handling errors. This was time-consuming, but it helped me to uncover issues that may not be apparent from automated testing alone.

### Boxuan Hu

I tested my code by printing out the received html content and do the check mannually. When extracting cookies and tokens, I will print out both received html content and cookies to see if they are matched. When writing code to log in user, I print out the html content, if it’s a webpage containing friends’ name and links, then it’s successful, otherwise, something goes wrong.

The biggest challenge I faced is extracting cookies and tokens from response messages. I have to manipulate the strings and manually try again and again to find the correct way to extract credentials in the correct format.

### Kan Zhou

I am currently using a match loop to match tags in my code, but I am facing some challenges in regards to posting and getting protocols. I have tested my code using various other codes.
