from unittest import TestCase
from collections import defaultdict
from yogaDownload import *

class Tests(TestCase):
    def test_instructor(self):

        URL2 = 'https://www.yogadownload.com/Utilities/InstructorProfiles/tabid/111/profileid/500/'
        session = setup_connection()
        instructors = defaultdict(Instructor)
        instructors = update_instructor(URL2, instructors, session)
        self.assertEqual("Ben Davis", instructors[500].name)