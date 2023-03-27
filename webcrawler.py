#!/usr/bin/env python3

import cgi
import socket
import sys
import ssl
from collections import deque
from html.parser import HTMLParser

# global variables
CRLF = "\r\n"

# use a dara structure to track unique URLs already crawled
crawled_page = set()
# use a dara structure to track URLs to be crawled
not_crawled_page = deque()
# use a dara structure to store unique secret flags found in the pages
secret_flags = set()
# use a dara structure to hold the middlewaretoken
token = list()


class FakebookHTMLParser(HTMLParser):
    """
    The FakebookHTMLParser extends the HTML Parser to parse through the server response for tags in search of
    more URLs and/or secret flags respectively.
    You can write code for the following tasks
    - look for the links in the HTML code that you will need to crawl, next.
    - look for the secret flags among tags, and process tham
    - look for the csrfmiddlewaretoken, and process it.
    """

    def __init__(self):
        super().__init__()    
        self.is_h2 = False
        self.h2_data = ''
        self.csrfmiddleware_token = False

    def handle_starttag(self, tag, attrs):
        match tag:
            case 'a':  
                for attr in attrs:
                    if attr[1].startswith("/fakebook"):
                        not_crawled_page.append(attr[1])  

            case "h2":  
                for attr in attrs:
                    if "secret_flag" in attr:  
                        self.is_h2 = True

            case 'input':
                for attr in attrs:
                    if self.csrfmiddleware_token:  
                        token.append(attr[1])
                        self.csrfmiddleware_token = False
                    if attr[1] == "csrfmiddlewaretoken":  
                        self.csrfmiddleware_token = True

    def handle_endtag(self, tag):
        if tag == 'h2':  
            self.is_h2 = False
            if self.h2_data != '':  
                flag = self.h2_data.split()[1]
                if flag not in secret_flags:
                    secret_flags.add(flag)  
                    print(flag)
            self.h2_data = ''  

    def handle_data(self, data):
        if self.is_h2:
            self.h2_data += data
            
# Parses the command line arguments for username and password. Throws error for invalid info
def parse_cmd_line():
    username = ""
    password = ""

    try:
        username = sys.argv[1]
        password = sys.argv[2]
        return username, password

    except:
        if username == "":
            sys.exit("Please provide appropriate user name.")
        if password == "":
            sys.exit("Please provide appropriate password.")


def create_socket():
    """Creates a TLS wrapped socket to create a connection to http server. """
    port = 443
    host_name = 'project2.5700.network'

    # building connection
    try:
        context = ssl.create_default_context()
        sock = socket.create_connection((host_name, port))
        wrapped_socket = context.wrap_socket(sock, server_hostname='project2.5700.network')
        return wrapped_socket
    except socket.error:
        sys.exit("Connection error.")


# this function will help you send the get request
def send_get_request(path, sock, host, cookie1=None, cookie2=None):
    """
    write code to send request along with appropriate header fields, and handle cookies. Send this header
    file to the server using socket
    """

    headers = ["GET " + path + " " + "HTTP/1.1", host]
    cookie_header = ""
    if (cookie1 != None):
        cookie_header += 'Cookie: csrftoken=' + cookie1
        if (cookie2 != None):
            cookie_header += "; " + 'sessionid=' + cookie2
        headers.append(cookie_header)
    request = CRLF.join(headers) + CRLF + CRLF
    sock.send(request.encode())


# this function will help you to receive message from the server for any request sent by the client

def receive_msg(sock):
    """
    Receive the message in a loop based on the content length given in the header
    """
    msg = sock.recv(4096).decode()
    length = getContent_length(msg)
    while True:
        if length == "0":
            break
        elif not msg.endswith('</html>\n'):
            msg += sock.recv(4096).decode()
        else:
            break
    return msg
    
    
def getContent_length(msg):
    """Extracts the content length of the URL"""
    if "Content-Length:" in msg:
        m = msg.split()
        idx = m.index("Content-Length:")
        length = m[idx + 1]
        return length


# this function will help you to extract cookies from the response message
def cookie_jar(msg):
    """
    Stores the session and/or the csrf cookies
    return cookies
    """
    header_end = msg.rfind(CRLF + CRLF)
    headers = msg[:header_end].split(CRLF)

    session_cookie = None
    csrf_cookie = None

    for header in headers:
        if header.startswith("Set-Cookie: sessionid"):
            session_cookie = header.split(';')[0].split('=')[1].strip()
        if header.startswith("Set-Cookie: csrftoken"):
            csrf_cookie = header.split(';')[0].split('=')[1].strip()

    return session_cookie, csrf_cookie


# this function will help you to send the  request to login
def login_user(sock, path, host, body_len, body, cookie1, cookie2=None):
    """
    create a  request and send it to login to the fakebook site
    """
    login_headers = ["POST " + path + " " + "HTTP/1.1", host,
                     'Cookie: csrftoken=' + cookie1,
                     'Content-Type: application/x-www-form-urlencoded',
                     'Content-Length: ' + str(body_len)]
    login_body = CRLF.join(login_headers) + CRLF + CRLF + body + CRLF + CRLF
    sock.send(login_body.encode())
    return receive_msg(sock)


def redirect_page(msg):
    """
    get redirected page
    """
    msg = msg.partition(CRLF + CRLF)
    headers = msg[0]
    redirected_page = ""
    for header in headers.split(CRLF):
        if header.startswith("Location: "):
            redirected_page = header.split()[1]
    return redirected_page


def get_res(msg):
    """
    covert response code to integer
    """
    res_code = 500
    if len(msg) > 0:
        res_code = int(msg.splitlines()[0].split()[1])
    return res_code
    

def start_crawling(msg, sock, host, cookie3, cookie4):
    """
    Implements the basic web crawler for this program.
    You can use the HTML Parser object to parse through the current URL in search for more URLs and/or secret flags until all
    secret flags are found for the user.
    Also accounts for and appropriately handles different errors received when parsing through pages.
    """
    parser = FakebookHTMLParser()

    parser.feed(msg)

    while len(not_crawled_page) != 0:
        temp = not_crawled_page.popleft()


        if temp not in crawled_page:
            send_get_request(temp, sock, host, cookie1=cookie3, cookie2=cookie4)
            msg = receive_msg(sock)
            res = get_res(msg)

            # response ok 200 - pass

            if res in range(200, 299):
                pass

            # 300 - redirect page
            elif res in range(300, 399):
                redirected_page = redirect_page(msg)
                if redirected_page != "":
                    not_crawled_page.append(redirected_page)
                    
            # 400
            elif res in range(400, 499):

                crawled_page.add(temp)
                continue

            # 500
            elif res in range(500, 599 + 1):
                not_crawled_page.append(temp)
                continue

            parser.feed(msg)
            crawled_page.add(temp)
            if len(secret_flags) == 5:
                break


def main():
    host = "Host: project2.5700.network"
    root_path = "/"
    fakebook = "/fakebook/"
    login_path = "/accounts/login/?next=/fakebook/"

    # Parse the username and password from the command line
    username, password = parse_cmd_line()
    # print("Username: " + username, "Password: " + password)

    # Create TLS wrapped socket
    wrapped_socket = create_socket()

    # get the root page
    send_get_request(root_path, wrapped_socket, host)

    # check the received message
    received_message_root_page = receive_msg(wrapped_socket)

    # store session cookie
    session_cookie, csrf_cookie = cookie_jar(received_message_root_page)

    # send get request for login page
    send_get_request(login_path, wrapped_socket, host)

    # check message for login page
    received_message_login_page = receive_msg(wrapped_socket)

    # retrieving csrf cookie and middleware token
    session_cookie_login, csrf_cookie_login = cookie_jar(received_message_login_page)
    parser = FakebookHTMLParser()
    parser.feed(received_message_login_page)
    # using token from token list
    csrfmiddleware_token = token[0]

    # creating login body for user
    login_content = ['username=' + username, 'password=' + password,
                     'csrfmiddlewaretoken=' + csrfmiddleware_token,
                     'next=%2Ffakebook%2F']
    login_content = "&".join(login_content)

    # login user
    received_message_login_page = login_user(wrapped_socket, login_path, host, len(login_content),
                                             login_content, csrf_cookie_login)

    # store new cookies
    session_cookie_login, csrf_cookie_login = cookie_jar(received_message_login_page)

    # send request to go to my fakebook page
    send_get_request(fakebook, wrapped_socket, host, csrf_cookie_login,
                     session_cookie_login)
    received_message_fakebook_page = receive_msg(wrapped_socket)
    # print("Fakebook page: ", received_message_fakebook_page)

    # start your crawler
    start_crawling(received_message_fakebook_page, wrapped_socket, host, csrf_cookie_login, session_cookie_login)

    # close the socket - program end
    wrapped_socket.close()



if __name__ == "__main__":
    main()
