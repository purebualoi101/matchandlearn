from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.auth.models import User
from tinderforeduapp.models import Userinfo, Subject, MatchedName
from selenium.webdriver.support.ui import Select
import time

# Create your tests here.
class CommentTest(LiveServerTestCase):

    def setUp(self):
        # open Firefox.
        self.browser = webdriver.Firefox()
        # create user for login.
        User.objects.create_user('johnny01', 'john@email.com', 'johnnypassword')
        User.objects.create_user(username='stefanie01', email='stefanie@email.com', password='stefaniepass')
        User.objects.create_user('eric01', 'eric@email.com', 'ericpassword')
        # create users that use website.
        john = Userinfo.objects.create(name='johnny01', first_name='John', last_name='Snow',
                                age='20', school='kmutnb', gender='Male')
        stefanie = Userinfo.objects.create(name='stefanie01', first_name='Stefanie', last_name='Walker',
                                age='21', school='kmutnb', gender='Female')
        eric = Userinfo.objects.create(name='eric01', first_name='Eric', last_name='Runner',
                                age='22', school='kmutnb', gender='Male')

        # John pair with Stefanie.
        MatchedName.objects.create(myself='johnny01', match='stefanie01')
        john_match_first = MatchedName.objects.get(myself='johnny01', match='stefanie01')
        john.match.add(john_match_first)
        MatchedName.objects.create(myself='stefanie01', match='johnny01')
        stefanie_match = MatchedName.objects.get(myself='stefanie01', match='johnny01')
        stefanie.match.add(stefanie_match)

        # John pair with Stefanie.
        MatchedName.objects.create(myself='johnny01', match='eric01')
        john_match_second = MatchedName.objects.get(myself='johnny01', match='eric01')
        john.match.add(john_match_second)
        MatchedName.objects.create(myself='eric01', match='johnny01')
        eric_match = MatchedName.objects.get(myself='eric01', match='johnny01')
        eric.match.add(eric_match)

    def tearDown(self):
        self.browser.quit()

    def test_can_send_comment_and_comment_receiver_can_see_it(self):
        # Stefanie login website.
        self.browser.get('http://127.0.0.1:8000/login/')
        username_textbox = self.browser.find_element_by_id("id_username")
        username_textbox.send_keys('stefanie01')
        password_textbox = self.browser.find_element_by_id("id_password")
        password_textbox.send_keys('stefpass')
        password_textbox.send_keys(Keys.ENTER)
        time.sleep(2)

        # She wants to comment to John. She clicks "Student and Tutor list".
        st_link = self.browser.find_element_by_link_text('Students and Tutor list')
        st_link.click()
        time.sleep(2)

        # She sees John name and click it.
        John_link = self.browser.find_element_by_css_selector('div.subDiv')
        John_link.click()
        time.sleep(2)

        # She sees comment textbox, dropdown score and submit button.
        comment_textbox = self.browser.find_element_by_id('id_comment')
        dropdown_score = Select(self.browser.find_element_by_id('id_star'))
        submit_btn = self.browser.find_element_by_id('id_submit_comment')

        # She found that John had no comment at all.
        num_comment = self.browser.find_element_by_id('id_num_comment').text
        self.assertEqual(num_comment, '0 comments')

        # She types comment in comment textbox and selects 5 score in dropdown score.
        comment_textbox.send_keys('John is so smart. I got an A in Math because of him')
        time.sleep(2)
        dropdown_score.select_by_value('5')
        time.sleep(2)

        # She click submit button.
        submit_btn.click()
        time.sleep(4)

        # She sees comment that she sent to John.
        num_comment = self.browser.find_element_by_id('id_num_comment').text
        self.assertEqual(num_comment, '1 comments')

        stefanie_comment = self.browser.find_element_by_class_name('comments').text
        self.assertIn('stefanie01', stefanie_comment)
        self.assertIn('Comment : John is so smart. I got an A in Math because of him', stefanie_comment)
        self.assertIn('Star : 5', stefanie_comment)
        time.sleep(2)

        # John login website.
        self.browser.get('http://127.0.0.1:8000/login/')
        username_textbox = self.browser.find_element_by_id("id_username")
        username_textbox.send_keys('john01')
        password_textbox = self.browser.find_element_by_id("id_password")
        password_textbox.send_keys('johnpass')
        password_textbox.send_keys(Keys.ENTER)
        time.sleep(2)

        # He wants to see comment. He clicks his profile link.
        profile_link = self.browser.find_element_by_link_text('Profile : John')
        profile_link.click()
        time.sleep(2)

        # He sees 1 comment of Stefanie.
        num_comment = self.browser.find_element_by_id('id_num_commentuser').text
        self.assertEqual(num_comment, '1 comments')
        stefanie_comment = self.browser.find_element_by_class_name('comments').text
        self.assertIn('stefanie01', stefanie_comment)
        self.assertIn('Comment : John is so smart. I got an A in Math because of him', stefanie_comment)
        self.assertIn('Star : 5', stefanie_comment)
        time.sleep(2)