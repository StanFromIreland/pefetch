import argparse
import urllib.request
import urllib.error
from html.parser import HTMLParser


class Stripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.current_href = None

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href')
            if href:
                self.current_href = "https://projecteuler.net/" + href.lstrip("/")

    def handle_endtag(self, tag):
        if tag == 'a' and self.current_href:
            self.current_href = None

    def handle_data(self, data):
        if self.current_href:
            self.result.append(f"{data} [\u001b[34;1m{self.current_href}\u001b[0m]")
        else:
            self.result.append(data)

    def get_text(self):
        return ''.join(self.result)


def strip_html(html):
    parser = Stripper()
    parser.feed(html)
    return parser.get_text()


def latexizer(string):
    string = string.replace('$$', '$')
    OPENING_DLLR = True
    result = []
    for char in string:
        if char == '$':
            if OPENING_DLLR:
                result.append('\u001b[37;1m')
            else:
                result.append('\u001b[0m')
            OPENING_DLLR = not OPENING_DLLR
        else:
            result.append(char)

    string = ''.join(result)
    string = string.replace('\\dots', '...')
    string = string.replace('\\times', '*')
    return string


def format_content(content, number):
    result = f"\033[1m\u001b[36;1mProject Euler Problem {number}\n\u001b[0m"
    content = content.strip()
    content = strip_html(content)
    content = latexizer(content)
    result += content
    lines = result.splitlines()
    return result


def fetch_problem(number):
    url = f"https://projecteuler.net/minimal={number}"
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8')
            print(format_content(content, number))
    except urllib.error.HTTPError as e:
        print(f"Error: Could not fetch problem {number} (HTTP {e.code})")
    except urllib.error.URLError as e:
        print(f"Error: Failed to reach server: {e.reason}")


def main():
    parser = argparse.ArgumentParser(
        prog='pefetch',
        description='Project Euler Problem Fetcher',
        epilog='https://github.com/StanFromIreland/pefetch',)
    parser.add_argument('problem')
    parser.add_argument('--link', '-l', action='store_true')
    args = parser.parse_args()

    fetch_problem(args.problem)

    if args.link:
        print(f"\n\u001b[34;1mhttps://projecteuler.net/problem={args.problem}\n\u001b[0m")
