import mechanicalsoup
import requests
import time
import threading
import sys
import math
from tldextract import extract
from argparse import ArgumentParser, ArgumentError
from typing import List, Set, Dict, Tuple, Optional, Union, Any
from rich.console import Console

console = Console()
error_console = Console(stderr=True, style="bold red")

class Crawlytics:
    """
    Crawlytics class

    Args:
        hostname (str): Hostname of the website

    Attributes:
        __start (float): Time at which the crawler was started
        __browser (mechanicalsoup.StatefulBrowser): Browser object
        user_agent (str): User agent
        _crawl_url_limit (int): URL limit for crawling (default = 1000)
        _url_flag_limit (bool): URL limit flag
        __thread_time_limit (int): Time limit in minutes for thread (default = 20)
        __time_flag_limit (bool): Time limit flag
        time_break_limit (int): Time limit in minutes for break (default = 5 min)
        __threads_limit (int): Limit for threads (default = 100)
        __threads_buffer (Set[str]): Thread buffer for new threads to be created (Threads Limit)
        thread_kill (bool): Thread kill flag
        __thread_flag_limit (bool): Thread flag limit (Stop creating new threads)
        _hostname (str): Hostname of the website
        _domain (str): Domain name of the website
        __fetched_urls (List[str]): URLs fetched from the webpages
        _known_extensions (List[str]): Extensions to be crawled (eg. php, html, htm, aspx, jsp)
        _ignore_extensions (List[str]): Extensions to be ignored while crawling (eg. png, jpeg, jpg, js, css, gif, pdf)
        __session_end_phrases (List[str]): Session end phrases if present in the URL then don't crawl it (eg. logout, sign out, log-out)
        __non_page_href (List[str]): Non-page URLs to be ignored while crawling (eg. javascript, mailto, tel)
        _fetched_urls (Set[str]): Fetched URLs
        __processed_urls (Set[str]): Processed URLs
        __logout_page (str): Login and logout pages
        thread (threading.Thread): Thread object
    """

    def __init__(self, hostname: str, url_limit: int = 1000):
        """
        Constructor method
        """
        # Time at which the crawler was started
        self.__start: float = time.time()

        # Browser object
        self.__browser: mechanicalsoup.StatefulBrowser = mechanicalsoup.StatefulBrowser()

        # User agent
        self.user_agent: str = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36 Firefox/62.0"
        )
        # URL limit for crawling (default = 1000)
        self._crawl_url_limit: int = url_limit
        self._url_flag_limit: bool = False

        # Time limit in minutes for thread (default = 20)
        self.__thread_time_limit: int = 20 * 60
        # Time limit flag
        self.__time_flag_limit: bool = False

        # Time limit in minutes for break (default = 5 min)
        self.time_break_limit: int = 300

        # Limit for threads (default = 100)
        self.__threads_limit: int = 100

        # Thread buffer for new threads to be created (Threads Limit)
        self.__threads_buffer: Set[str] = set()

        # Thread kill flag
        self.thread_kill: bool = False

        # Thread flag limit (Stop creating new threads)
        self.__thread_flag_limit: bool = False

        # Hostname of the website
        self._hostname: str = requests.get(hostname).url

        # Domain name of the website
        self._domain: str = self.get_domain_name(self._hostname)

        # URLs fetched from the webpages
        self.__fetched_urls: List[str] = []

        # Extensions to be crawled (eg. php, html, htm, aspx, jsp)
        self._known_extensions: List[str] = [
            'php', 'html', 'htm', 'aspx',
            'jsp', 'dj', 'asp', 'py','vb',
            'vbjx', 'servlet', 'sql','ts'
        ]

        # Extensions to be ignored while crawling (eg. png, jpeg, jpg, js, css, gif, pdf)
        self._ignore_extensions: List[str] = [
            'png', 'javascript', 'jpeg', 'jpg',
            'js', 'css','gif', 'tif', 'bmp', 'ppm',
            'webp', 'svg', 'pdf', 'ico', 'pdf',
            'xlsx', 'csv', 'exe', 'war', 'mp4'
        ]

        # Session end phrases if present in the URL then don't crawl it (eg. logout, sign out, log-out)
        self.__session_end_phrases: List[str] = [
            "logout", "log out", "log-out", "log_out",
            "signout", "sign out","sign-out", "sign_out",
            "logoff", "log-off", "log off", "log_off",
            "signoff", "sign-off", "sign off", "sign_off"
        ]

        # Non-page URLs to be ignored while crawling (eg. javascript, mailto, tel)
        self.__non_page_href: List[str] = ['javascript:','mailto:','tel:']

        # Fetched URLs
        self._fetched_urls: Set[str] = set()
        # Processed URLs
        self.__processed_urls: Set[str] = set()

        # Login and logout pages
        self.__logout_page: str = ''

        # Thread object
        self.thread: threading.Thread = None

    def thread_buffer(self, url: str) -> None:
        """
        Create a thread buffer for new threads to be created

        Args:
            url (str): URL to be added to the thread buffer
        """

        try:
            # Checking if the url is not in the thread buffer and adding it
            if url not in self.__threads_buffer:
                self.__threads_buffer.add(url)

        except Exception as error:
            error_console.print('thread buffer funtion error')
            error_console.print(error)

    def thread_create(self) -> None:
        """
        Create new threads when the thread limit is not reached
        """
        try:
            # Copying the thread buffer to a new variable
            thread_buffer: Set[str] = self.__threads_buffer.copy()

            # Checking if the thread buffer is not empty
            if len(thread_buffer) > 0:
                    # Checking if the thread limit is not reached and creating new threads
                    active_thread: int = threading.active_count()
                    if active_thread < self.__threads_limit:
                            new_thread_available: int  = self.__threads_limit - active_thread
                            # Checking if the thread buffer is less than the new threads available to be created
                            # If yes then create new threads for all the URLs in the thread buffer
                            if len(thread_buffer) < new_thread_available:
                                    # Creating new threads
                                    for url in thread_buffer:
                                        self.thread_start(url)
                                        self.__threads_buffer.remove(url)
                            # If no then create new threads for the URLs in the thread buffer till the new threads available to be created
                            else:
                                new_thread_url: List[str] = list(thread_buffer)[:new_thread_available]
                                # Creating new threads
                                for url in new_thread_url:
                                    self.thread_start(url)
                                    self.__threads_buffer.remove(url)

        except Exception as error:
            error_console.print('thread create function error')
            error_console.print(error)

    def thread_start(self, url: str) -> None:
        """
        Start a new thread for the URL

        Args:
            url (str): URL to be crawled
        """
        # Checking if the time limit is not reached and the URL limit is not reached
        if not self.__time_flag_limit and not self._url_flag_limit:
            try:
                self.thread = threading.Thread(target=self.crawl_url, args=(url,))
                self.thread.start()

            except Exception as error:
                error_console.print('Thread Function Error')
                error_console.print(error)

    def get_domain_name(self, url: str) -> str:
        """
        Get domain name (example.com)
        This function return the domain/subdomain on the basis of url
        Ex- http://example.com/url => example.com
        http://sub.examole.com/url => sub.example.com

        Args:
            url (str): URL to get the domain name from

        Returns:
            str: Domain name
        """
        domain: str = ''
        if 'http' in url:
            domain = url.split('://',1)[1]
        count = domain.count('/')
        if count > 0:
            domain = domain.split('/',count)[0]
        return domain

    def verify_scope_url(self, url: str) -> str|None:
        """
        Verify if the URL is in scope or not

        Args:
            url (str): URL to be verified

        Returns:
            str: URL if it is in scope else None
        """
        if url:
            if 'http' in url:
                if self._domain in self.get_domain_name(url):
                    return url
        return None

    def reference_url(self, url: str, start_url: str, browser: mechanicalsoup.StatefulBrowser) -> str|None:
        """
        Convert the reference url to absolute url

        Args:
            url (str): Reference url
            start_url (str): Starting url (current page for this reference url)
            browser (mechanicalsoup.StatefulBrowser): Browser object

        Returns:
            str: Absolute url
        """
        try:
            # Checking if the url is not empty and not a hash tag
            if url[0] != '#' and not self.thread_kill and url:

                # Opening the starting url (current page for this reference url) in the browser
                browser.open(start_url)

                # Opening the reference url in the browser
                # Generating urls from relative urls
                resp = browser.open_relative(url)

                if 200 >= resp.status_code <= 400:
                    return resp.url

        except requests.exceptions.ConnectionError:
            time.sleep(10)
            pass

        except Exception as error:
            error_console.print('Reference url function error')
            error_console.print(error)

        return None

    def crawl_url(self, start_url: str) -> None:
        """
        Crawl the urls on the web page and add them to the thread buffer

        Args:
            start_url (str): Starting url
        """
        try:

            fetched_urls: Set[str] = set()

            # Opening the starting url in the browser
            self.__browser.open(start_url)

            try:
                # Getting all the urls from the current page
                all_urls_tag = self.__browser.links()

            except:
                # If the current page is not a web page (doesn't contain any html content)
                all_urls_tag = None

            if all_urls_tag:
                # Iterating through all the urls
                for url_tag in all_urls_tag:

                    # Checking if the thread kill flag is not set
                    if not self.thread_kill:

                        # Initializing the variables
                        url = None
                        href_value = url_tag.attrs['href']
                        logout = False
                        not_page = False
                        ignore = False

                        # Checking if the url is not empty and not a hash tag
                        if href_value and href_value[0] != '#':
                            # Checking if the url is not a logout page
                            for logout_page in self.__session_end_phrases:
                                if str(logout_page).lower() in str(href_value).lower():
                                    logout = True
                                    # Setting the logout page
                                    if self.__logout_page is None:
                                        self.__logout_page = str(href_value)

                            # Checking if the url is not a non page url (eg. javascript, mailto, tel)
                            for not_a_page in self.__non_page_href:
                                if str(not_a_page) in str(href_value).lower():
                                    not_page = True

                            # Checking if the url is not an ignored extension
                            if len(href_value)> 4:
                                for ignore_extension in self._ignore_extensions:
                                        if ignore_extension in  href_value[-4:] and '=' not in href_value and '?' not in href_value:
                                            ignore = True

                            if not logout and not not_page and not ignore:

                                # Checking if the url is a relative url
                                if 'http' not in href_value:
                                    # Converting the relative url to absolute url
                                    url = self.reference_url(href_value, start_url, self.__browser)
                                else:
                                    url = href_value

                                # Verifying if the url is in scope or not
                                if url:
                                    url = self.verify_scope_url(url)


                                # Adding the url to the fetched urls
                                if url:
                                    fetched_urls.add(url)

            # Adding the fetched urls to the fetched urls list
            self.__fetched_urls.extend(fetched_urls)

            # Adding the fetched urls to the thread buffer if they are not already processed
            for fetched_url in fetched_urls:
                if fetched_url not in self.__processed_urls:
                    # Adding the fetched url to the processed urls set
                    self.__processed_urls.add(fetched_url)
                    # Adding the fetched url to the thread buffer if the thread kill flag is not set
                    if not self.__time_flag_limit:
                        self.thread_buffer(fetched_url)


        except requests.exceptions.ConnectionError:
            time.sleep(10)

        except Exception as error:
            error_console.print('crawl url function error')
            error_console.print(error)

    def crawl_site(self, start_url: str) -> List[str]:
        """
        Main crawling function which starts the crawling process and maintains the threads

        Args:
            start_url (str): Starting url

        Returns:
            List[str]: List of all the crawled urls
        """

        # Initializing the variables
        self.__processed_urls: Set[str] = set()
        self.__processed_urls.add(start_url)
        self.thread_start(start_url)
        thread_count_backup: int = 0
        last_update_time: float = time.time()

        with console.status('[bold green]Crawling...'):
            # Looping until all the threads are completed
            while threading.active_count() > 1  or len(self.__threads_buffer) > 0:
                try:
                    # Updating the thread count
                    thread_count: int = threading.active_count()
                    thread_enum: int = len(threading.enumerate())

                    # Checking for time limit, if time limit exceed then sudden break out of loop
                    if self.__time_flag_limit and int(time.time()) > int(self.time_break_limit):
                        break

                    if len(self.__processed_urls) >= self._crawl_url_limit and self._url_flag_limit == False:
                        console.print('[bold yellow] Url Limit Reached[/bold yellow]')
                        self._url_flag_limit = True

                    # Update terminal output when thread count has changed or 20s have passed
                    if thread_count_backup != thread_count or int(time.time()) - int(last_update_time) > 20:
                        last_update_time: float = time.time()
                        thread_count_backup: int = thread_count

                        # Calculating the time elapsed since the start of crawling
                        secs = time.time() - self.__start
                        hours = math.floor(secs/3600)
                        secs = secs-(hours*3600)
                        mins = math.floor(secs/60)
                        secs = math.floor(secs-(mins*60))

                        # Updating the terminal output with the current status of the crawling process
                        console.print('['+str(hours)+':'+str(mins)+':'+str(secs)+'] Visited URLs '+str(len(self.__processed_urls))+' Threads '+str(thread_count)+' Fetched URLs '+str(len(self.__fetched_urls))+'   ')

                    # Checking if the thread buffer is not empty if yes then create a new thread
                    if len(self.__threads_buffer) > 0:
                        self.thread_create()

                        # Updating the thread count
                        thread_count: int = threading.active_count()
                        thread_enum: int = len(threading.enumerate())

                    if (thread_count > 1 or thread_enum > 1) and not self.__time_flag_limit and not self._url_flag_limit:

                        # Checking if the thread time limit is reached or not
                        if (time.time() - self.__start > self.__thread_time_limit):

                            # If time limit is reached then wait for all the threads to join
                            print('Time Limit Reached. Waiting for thread Join(5 min)')
                            self.__time_flag_limit = True
                            self.thread_kill = True
                            self.time_break_limit += int(time.time())

                        else:
                            self.thread_create()
                            thread_count = threading.active_count()
                            thread_enum = len(threading.enumerate())

                    else:
                        #checking if all threads are finished and thread_buffer is also empty then break out of loop
                        if len(self.__threads_buffer) == 0 and (threading.active_count() == 1 and len(threading.enumerate()) == 1):
                            break

                except Exception as error:
                    error_console.print('crawl site function error')
                    error_console.print(error)
                    pass

        console.print(f'[bold green] Complete execution: [/][bold blue]Total Visited URls: {len(self.__processed_urls)}[/]')
        return self.__processed_urls


def get_hostname(url: str) -> str:
    """
    Get the hostname from the URL.

    Args:
        url (str): The URL of the website to check

    Returns:
        str: The hostname
    """
    #Check if the URL starts with HTTP or HTTPS
    if not url.startswith('http'):
        # If not, add the HTTP scheme
        hostname = f"http://{url}"
    else:
        hostname = url

    return hostname

def parse_args() -> ArgumentParser:
    """
    Parse the command line arguments.
    """
    # Initialize the argument parser
    parser = ArgumentParser(
        prog = "crawlytics",
        description = "Crawlytics is a python script which crawls the website and fetches all the URLs present on the website.",
        epilog = "Example: python3 crawlytics.py -u https://www.breachlock.com [-l 1000]"
    )
    parser.add_argument("-u", "--url", type=str, dest="url", required=True, help="Provide the URL to check")
    parser.add_argument("-l", "--url_limit", type=int, dest="url_limit", default=1000, help="Provide URL limit to crawl (default: 1000)")
    return parser.parse_args()

def main():
    """
    Main function which calls the crawler object and starts the crawling process.
    """
    try:

        # Parse the command line arguments
        args: ArgumentParser = parse_args()
        hostname: str = get_hostname(args.url)
        url_limit: int = args.url_limit

        # Creating the crawler object
        crawler_obj = Crawlytics(hostname, url_limit)
        crawl_urls: Set[str] = set()

        crawl_urls = crawler_obj.crawl_site(hostname)

        # Printing the crawled urls
        console.print('\n')
        console.print("***********************Crawled URL*********************** "+' Total URls: '+str(len(crawl_urls)))
        for url in crawl_urls:
            console.print(f'[bold blue] {url} [/bold blue]')
        console.print('***********************Crawling Complete***********************')

    except ArgumentError as arg_error:
        error_console.print(f'Error: {arg_error}')
        sys.exit(0)
    except Exception as error:
        error_console.print('Main function Error')
        error_console.print(error)

if __name__ == '__main__':
    main()