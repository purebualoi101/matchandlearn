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
        
    def tearDown(self):
        self.browser.quit()

    def login(self, username, password):
        username_textbox = self.browser.find_element_by_id("id_username")
        username_textbox.send_keys(username)
        password_textbox = self.browser.find_element_by_id("id_password")
        password_textbox.send_keys(password)
        password_textbox.send_keys(Keys.ENTER)
        time.sleep(2)

    def test_can_send_comment_and_comment_receiver_can_see_it(self):
        # Stefanie login website.
        self.browser.get('http://127.0.0.1:8000/login/')
        self.login('stefanie01', 'stefpass')

        # She wants to comment to John. She clicks "Student and Tutor list".
        st_link = self.browser.find_element_by_link_text('Students and Tutor list')
        st_link.click()
        time.sleep(2)

        # She sees John name and click it.
        john_link = self.browser.find_element_by_id('id_name_list_john01')
        john_link.click()
        time.sleep(2)

        # She sees comment textbox, dropdown score and submit button.
        comment_textbox = self.browser.find_element_by_id('id_comment')
        dropdown_score = Select(self.browser.find_element_by_id('id_star'))
        submit_btn = self.browser.find_element_by_id('id_submit_comment')

        # She found that John had no comment at all.
        num_comment = self.browser.find_element_by_id('id_num_comment').text
        self.assertEqual(num_comment, '0 Reviews')

        # She types comment in comment textbox and selects 5 score in dropdown score.
        comment_textbox.send_keys('John is so smart. I got an A in Math because of him')
        time.sleep(2)
        dropdown_score.select_by_value('5')
        time.sleep(2)

        # She click submit button.
        submit_btn.click()
        time.sleep(4)

        # Page refresh.
        # She sees comment that she sent to John.
        num_comment = self.browser.find_element_by_id('id_num_comment').text
        self.assertEqual(num_comment, '1 Reviews')

        stefanie_comment = self.browser.find_element_by_id('id_comment_stefanie01').text
        self.assertIn('stefanie01', stefanie_comment)
        self.assertIn('Comment : John is so smart. I got an A in Math because of him', stefanie_comment)
        self.assertIn('Star : 5', stefanie_comment)
        time.sleep(2)

        # John login website.
        self.browser.get('http://127.0.0.1:8000/login/')
        self.login('john01', 'johnpass')

        # He wants to see comment. He clicks his profile link.
        profile_link = self.browser.find_element_by_link_text('Profile : John')
        profile_link.click()
        time.sleep(2)

        # He sees 1 comment of Stefanie.
        num_comment = self.browser.find_element_by_id('id_num_commentuser').text
        self.assertEqual(num_comment, '1 comments')
        stefanie_comment = self.browser.find_element_by_id('id_comment_stefanie01').text
        self.assertIn('stefanie01', stefanie_comment)
        self.assertIn('Comment : John is so smart. I got an A in Math because of him', stefanie_comment)
        self.assertIn('Star : 5', stefanie_comment)
        time.sleep(2)

    def test_can_remove_review(self):
        # Stefanie login website.
        self.browser.get('http://127.0.0.1:8000/login/')
        self.login('stefanie01', 'stefpass')

        # She wants to comment to John. She clicks "Student and Tutor list".
        st_link = self.browser.find_element_by_link_text('Students and Tutor list')
        st_link.click()
        time.sleep(2)

        # She sees John profile link and click it.
        john_link = self.browser.find_element_by_id('id_name_list_john01')
        john_link.click()
        time.sleep(2)

        # She sees comment textbox, dropdown score and submit button.
        comment_textbox = self.browser.find_element_by_id('id_comment')
        dropdown_score = Select(self.browser.find_element_by_id('id_star'))
        submit_btn = self.browser.find_element_by_id('id_submit_comment')

        # She types comment in comment textbox and selects 5 score in dropdown score.
        comment_textbox.send_keys('John is so smart. I got an A in Math because of him')
        time.sleep(2)
        dropdown_score.select_by_value('5')
        time.sleep(2)

        # She click submit button.
        submit_btn.click()
        time.sleep(4)

        # Page refresh.
        # She sees comment that she sent to John.
        num_comment = self.browser.find_element_by_id('id_num_comment').text
        self.assertEqual(num_comment, '1 Reviews')

        stefanie_comment = self.browser.find_element_by_id('id_comment_stefanie01').text
        self.assertIn('stefanie01', stefanie_comment)
        self.assertIn('Comment : John is so smart. I got an A in Math because of him', stefanie_comment)
        self.assertIn('Star : 5', stefanie_comment)
        time.sleep(2)

        # She sees remove button and click it.
        remove_btn = self.browser.find_element_by_id('id_remove_comment')
        remove_btn.click()
        time.sleep(5)

        # Page refresh.
        num_comment = self.browser.find_element_by_id('id_num_comment').text
        self.assertEqual(num_comment, '0 Reviews')

        # She dose not see her review.
        review_section = self.browser.find_element_by_id('id_review_section').text
        self.assertNotIn('stefanie01', review_section)
        self.assertNotIn('Comment : John is so smart. I got an A in Math because of him', review_section)
        self.assertNotIn('Star : 5', review_section)


class LoginTest(LiveServerTestCase):

    def setUp(self):
        # open Firefox.
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_signup(self):
        # Jesse Lingard logins website.
        self.browser.get('http://127.0.0.1:8000/login/')
        time.sleep(2)

        # He does not have an account. So He click signup link.
        signup_link = self.browser.find_element_by_link_text('New to Match and Learn? Sign up now!')
        signup_link.click()
        time.sleep(2)

        # He types his info
        username = self.browser.find_element_by_id('id_username')
        username.send_keys('lingard14')
        password = self.browser.find_element_by_id('id_password1')
        password.send_keys('jlpassword')
        c_password = self.browser.find_element_by_id('id_password2')
        c_password.send_keys('jlpassword')
        first_name = self.browser.find_element_by_id('id_first_name')
        first_name.send_keys('Jesse')
        last_name = self.browser.find_element_by_id('id_last_name')
        last_name.send_keys('Lingard')
        age = self.browser.find_element_by_id('id_age')
        age.send_keys('27')
        gender = Select(self.browser.find_element_by_id('id_gender'))
        gender.select_by_value('Male')
        email = self.browser.find_element_by_id('id_email')
        email.send_keys('lingard@gmail.com')
        college = self.browser.find_element_by_id('id_college')
        college.send_keys('KMUTNB')
        time.sleep(2)

        # He clicks signup button.
        signup_btn = self.browser.find_element_by_tag_name('button')
        signup_btn.click()
        time.sleep(10)

        # He sees message about verify account.
        message = self.browser.find_element_by_tag_name('p').text
        self.assertIn('Please confirm your email address', message)
        self.assertIn('to complete the registration.', message)
        time.sleep(2)

        # He clicks Back to login link.
        login_link = self.browser.find_element_by_link_text('Back to login')
        login_link.click()
        time.sleep(2)

    def test_can_login(self):
        # Jesse Lingard wants to login "Match and Learn" website.
        self.browser.get('http://127.0.0.1:8000/login/')

        username_textbox = self.browser.find_element_by_id("id_username")
        username_textbox.send_keys('lingard14')
        password_textbox = self.browser.find_element_by_id("id_password")
        password_textbox.send_keys('jlpassword')
        password_textbox.send_keys(Keys.ENTER)
        time.sleep(2)


class SubjectTest(LiveServerTestCase):

    def setUp(self):
        # open Firefox.
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def login(self, username, password):
        username_textbox = self.browser.find_element_by_id("id_username")
        username_textbox.send_keys(username)
        password_textbox = self.browser.find_element_by_id("id_password")
        password_textbox.send_keys(password)
        password_textbox.send_keys(Keys.ENTER)
        time.sleep(2)

    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id('expert_subject_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])

    def can_add_expertise_subject(self):
        # Jesse Lingard login "Match and Learn" website.
        self.browser.get('http://127.0.0.1:8000/login/')

        self.login('lingard14', 'jlpassword')

        # He clicks his profile link to add expertise subject.
        lingard_link = self.browser.find_element_by_link_text('Profile : Jesse')
        lingard_link.click()
        time.sleep(2)

        # He types "physic" into "Add your expertise subject" textbox.
        subject_textbox = self.browser.find_element_by_id('subject_good_id')
        subject_textbox.send_keys('physic')
        time.sleep(2)

        # He clicks submit button to add expertise subject.
        submit_btn = self.browser.find_element_by_name('add_button')
        submit_btn.click()
        time.sleep(2)

        # the page show lists of his expertise subject.
        self.check_for_row_in_list_table('1: physic')

        # He types "math" into "Add your expertise subject" textbox.
        subject_textbox = self.browser.find_element_by_id('subject_good_id')
        subject_textbox.send_keys('math')
        time.sleep(2)
        submit_btn = self.browser.find_element_by_name('add_button')
        submit_btn.click()
        time.sleep(2)

        # the page show lists of his expertise subject.
        self.check_for_row_in_list_table('1: physic')
        self.check_for_row_in_list_table('2: math')

    def test_can_remove_expertise_subject(self):
        # Jesse Lingard login "Match and Learn" website.
        self.browser.get('http://127.0.0.1:8000/login/')
        self.login('lingard14', 'jlpassword')

        # He clicks his profile link to remove expertise subject.
        lingard_link = self.browser.find_element_by_link_text('Profile : Jesse')
        lingard_link.click()
        time.sleep(2)

        # He selects math checkbox to remove it
        table = self.browser.find_element_by_id('expert_subject_table')
        checkbox = table.find_element_by_id('subject_name:2')
        checkbox.click()
        remove_select = self.browser.find_element_by_id("remove_button_id")
        remove_select.send_keys(Keys.ENTER)
        time.sleep(2)
