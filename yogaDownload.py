from bs4 import BeautifulSoup
from collections import defaultdict

import pickle
import requests
import re

PRINT = True

URL = "https://www.yogadownload.com/Utilities/LoginExt/tabid/165/Default.aspx?returnurl=%2f"
STYLES = 'https://www.yogadownload.com/online-yoga-styles.aspx'
INSTRUCTORS = 'https://www.yogadownload.com/yogadownload-instructors.aspx'
PROGRAMS = 'https://www.yogadownload.com/yoga-online-programs-and-packages.aspx'
FOCI = 'https://www.yogadownload.com/yoga-online-classes-by-focus.aspx'
ALL = 'https://www.yogadownload.com/online-yoga-pilates-meditation-video-and-audio-classes.aspx'


class Class:
    id = None
    title = None
    instructor = None
    tags = []
    filters = []
    type = None
    lengths = []
    description = None

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '{} - {} by {}. Tags = {}'.format(self.id, self.title, self.instructor, self.tags)

class Instructor:
    id = None
    name = None
    site = None

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '{} - {}'.format(self.id, self.name)


def setup_connection():
    # start session
    session = requests.session()
    login_data = {'username': username, 'txtPassword': password, 'submit': 'login'}

    # Authenticate
    r = session.post(URL, data=login_data)
    return session

def main():
    session = setup_connection()

    # set up dicts
    classes = defaultdict(Class)
    instructors = defaultdict(Instructor)

    # loop through instructors
    r = session.get(INSTRUCTORS)
    soup = BeautifulSoup(r.content, 'lxml')

    instructorLinkPattern = '/Utilities/InstructorProfiles/tabid/111/profileid/(?P<profileid>\d+)/'
    for a in soup.findAll('a', {'href': re.compile(instructorLinkPattern)}):
        match = re.search(instructorLinkPattern, str(a))
        profileid = int(match.group('profileid'))
        instructors = update_instructor(profileid, instructors, classes, session)

    print(classes)

def update_instructor(profileid, instructors, classes, session):

    # get page
    inst_url = 'https://www.yogadownload.com/Utilities/InstructorProfiles/tabid/111/profileid/{}/'.format(profileid)
    r = session.get(inst_url)
    soup = BeautifulSoup(r.content, 'lxml')

    instructors[profileid] = Instructor(profileid)

    # name
    name = soup.h3.span.text.strip()
    instructors[profileid].name = name

    # classes
    classLinkPattern = '/Utilities/GenericProductDisplay/tabid/110/prodid/(?P<prodid>\d+)/default.aspx'
    for a in soup.findAll('a', {'href': re.compile(classLinkPattern)}):
        match = re.search(classLinkPattern, str(a))
        prodid = int(match.group('prodid'))
        classes = update_class(prodid, classes, session)

    return instructors

def update_class(prodid, classes, session):
    # get page
    class_url = 'https://www.yogadownload.com/Utilities/GenericProductDisplay/tabid/110/prodid/{}/default.aspx'.format(prodid)
    r = session.get(class_url)
    soup = BeautifulSoup(r.content, "lxml")

    # id
    classes[prodid] = Class(prodid)

    # title
    title = soup.h3.span.text
    classes[prodid].title = title

    # instructor
    instructor = soup.h4.a.text
    classes[prodid].instructor = instructor

    # description
    desc = soup.find('p', itemprop='description')
    desc = '\n'.join(str(item) for item in desc.contents)
    classes[prodid].description = desc

    # tags
    for tag in soup.findAll('span', 'ydl_category_alt'):
        classes[prodid].tags.append(tag.text)

    # filters
    for filter in soup.findAll('div', 'propitemnarrow'):
        classes[prodid].filters.append(filter.text)

    # class length
    for length in soup.findAll('td', text=re.compile(".+ \([0-9]+:[0-9]+\)")):
        classes[prodid].lengths.append(length.text)

    # type
    if soup.find('i', 'icon-video'):
        type = 'video'
    elif soup.find('i', 'icon-mic'):
        type = 'audio'
    classes[prodid].type = type

    return classes


if __name__ == '__main__':
    main()
