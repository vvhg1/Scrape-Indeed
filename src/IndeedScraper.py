import pandas as pd
import requests
from bs4 import BeautifulSoup

# this is a simple scraper, slapped together quickly rather than carefully engineered, so although it caters to my needs just fine,
# some adjustments might be advisable depending on use case.

# some variables, if the user does not enter anything when prompted, these act as defaults
search_term = "deep+learning"
area = "London,+Greater+London"
country = "uk"
pages = 1
# the list to which the extracted jobs are appended
jobs_list = []


def grab_page(page):
    """
    this takes an integer and returns the content of the search results
    page number specified by (page)
    """
    _headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'}
    url = f"https://{country}.indeed.com/jobs?q={search_term}&l={area}&sort=date&start=page{page}"
    _r = requests.get(url, _headers)
    _soup = BeautifulSoup(_r.content, 'html.parser')
    return _soup


def extract_desc(href):
    """
    this takes a href to the full job description, which lives on another page, hence the call
    and returns the full description
    """
    _headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'}
    url = f"https://{country}.indeed.com{href}"
    # print(f"concat url: {url}")
    r = requests.get(url, _headers)
    _soup = BeautifulSoup(r.content, 'html.parser')
    _job_description = _soup.find(
        'div', class_="jobsearch-jobDescriptionText").text.strip()
    return _job_description


def extract_info(soup):
    """
    this takes the return of grab_page(page), extracts the job info from the data and appends it to the jobs_list
    it also calls extract_desc(href) to get the full job description
    if the full description is not needed, the extract_desc(href) should be commented out, along with the corresponding line in the _job_item section, this will speed things up considerably
    """
    _divs = soup.find_all('div', class_='job_seen_beacon')
    for i in _divs:
        _job_title = i.find('a').text.strip()
        _full_description = extract_desc(i.find('a').get('href'))
        try:
            _company = i.find('span', class_='companyName').text.strip()
        except:
            # as not all listings provide this, it catches here and provides an empty string instead
            _company = ''
        _age_days = i.find('span', class_='date').text.strip()
        _short_description = i.find('div', class_='job-snippet').text.strip()
        try:
            _job_location = i.find(
                'div', class_='companyLocation').text.strip()
        except:
            # as not all listings provide this, it catches here and provides an empty string instead
            _job_location = ''

        _job_item = {
            'jobtitle': _job_title,
            'company': _company,
            'listed': _age_days,
            'joblocation': _job_location,
            'shortdescription': _short_description,
            'fulldescription': _full_description
        }
        jobs_list.append(_job_item)


def prompt_user_input(msg, myvar):
    """
    just a little helper to select user input or default
    """
    _uinput = input(msg)
    return _uinput if (_uinput != '') else myvar


# prompt for user input
search_term = prompt_user_input(
    "enter search_term, concat words with \"+\" (hit ENTER to select default): ", search_term)

area = prompt_user_input(
    "enter area (hit ENTER to select default): ", area)

country = prompt_user_input(
    "enter country, eg. \"de\" (hit ENTER to select default): ", country)

pages = int(prompt_user_input(
    "enter # of pages to search as integer (hit ENTER to select default): ", pages))
# this is the scraper loop, running for each page to scrape
# if the scraper reaches the end of available pages, it exits through the exception handling
for i in range(0, pages*10, 10):
    print(f"scraping page # {int(i/10)}")
    try:
        soup = grab_page(i)
        extract_info(soup)
    except:
        print('breaking out of scraping loop')
        break

# create a df and store the df as .json
jobs_dataframe = pd.DataFrame(jobs_list)
print(jobs_dataframe.head(40))
jobs_dataframe.to_json('data/jobs_list.json')
