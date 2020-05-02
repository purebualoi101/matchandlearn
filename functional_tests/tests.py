from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.auth.models import User
from tinderforeduapp.models import *
from selenium.webdriver.support.ui import Select
import time


# Create your tests here.
class CommentTest(LiveServerTestCase):

    def setUp(self):
        # open Firefox.
        self.browser = webdriver.Firefox()
        self.browser.maximize_window()

        # create users for login.
        john_login = User.objects.create_user('john01', 'john@email.com', 'johnpassword')
        john_login.first_name = 'John'
        john_login.last_name = 'Snow'
        john_login.save()
        stefanie_login = User.objects.create_user('stefanie01', 'stfanie@email.com', 'stefaniepassword')
        stefanie_login.first_name = 'Stefanie'
        stefanie_login.last_name = 'Walker'
        stefanie_login.save()
        eric_login = User.objects.create_user('eric01', 'eric@email.com', 'ericpassword')
        eric_login.first_name = 'Eric'
        eric_login.last_name = 'Runner'
        eric_login.save()

        # create users info.
        self.john = Userinfo.objects.create(name='john01', first_name='John', last_name='Snow', age='21',
                                            school='kmutnb')
        self.stefanie = Userinfo.objects.create(name='stefanie01', first_name='Stefanie', last_name='Walker', age='20',
                                                school='kmutnb')
        self.eric = Userinfo.objects.create(name='eric01', first_name='Eric', last_name='Runner', age='22',
                                            school='kmutnb')

        # create users profile picture.
        Profilepic.objects.create(user=self.john, images='default.png')
        Profilepic.objects.create(user=self.stefanie, images='default.png')
        Profilepic.objects.create(user=self.eric, images='default.png')

        # John pair with Stefanie.
        MatchedName.objects.create(myself='john01', match='stefanie01')
        john_stefanie = MatchedName.objects.get(myself='john01', match='stefanie01')
        self.john.match.add(john_stefanie)
        MatchedName.objects.create(myself='stefanie01', match='john01')
        stefanie_john = MatchedName.objects.get(myself='stefanie01', match='john01')
        self.stefanie.match.add(stefanie_john)

        # John pair with Eric.
        MatchedName.objects.create(myself='john01', match='eric01')
        john_eric = MatchedName.objects.get(myself='john01', match='eric01')
        self.john.match.add(john_eric)
        MatchedName.objects.create(myself='eric01', match='john01')
        eric_john = MatchedName.objects.get(myself='eric01', match='john01')
        self.eric.match.add(eric_john)

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
        self.browser.get(self.live_server_url)
        self.login('stefanie01', 'stefaniepassword')

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
        self.assertEqual(num_comment, '1 Reviews (Including your review)')

        stefanie_comment = self.browser.find_element_by_id('id_comment_stefanie01').text
        self.assertIn('stefanie01', stefanie_comment)
        self.assertIn('Comment : John is so smart. I got an A in Math because of him', stefanie_comment)
        self.assertIn('Star : 5', stefanie_comment)
        time.sleep(2)

        # She logout.
        logout = self.browser.find_element_by_link_text('Logout')
        logout.click()

        # John login website.
        self.browser.get(self.live_server_url)
        time.sleep(2)
        self.login('john01', 'johnpassword')

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
        self.browser.get(self.live_server_url)
        self.login('stefanie01', 'stefaniepassword')

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
        self.assertEqual(num_comment, '1 Reviews (Including your review)')

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
        self.browser.maximize_window()

    def tearDown(self):
        self.browser.quit()

    def test_can_signup_and_login(self):
        # Jesse Lingard logins website.
        self.browser.get(self.live_server_url)
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

        # He login to website.
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
        self.browser.maximize_window()

        # create users for login.
        john_login = User.objects.create_user('john01', 'john@email.com', 'johnpassword')
        john_login.first_name = 'John'
        john_login.last_name = 'Snow'
        john_login.save()

        # create users info.
        self.john = Userinfo.objects.create(name='john01', first_name='John', last_name='Snow', age='21',
                                            school='kmutnb')

        # create users profile picture.
        Profilepic.objects.create(user=self.john, images='default.png')

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

    def test_can_add_expertise_subject(self):
        # John login "Match and Learn" website.
        self.browser.get(self.live_server_url)
        self.login('john01', 'johnpassword')

        # He clicks his profile link to add expertise subject.
        john_link = self.browser.find_element_by_link_text('Profile : John')
        john_link.click()
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
        # John is good at physic and math.
        Subject.objects.create(subject_name='physic')
        physic = Subject.objects.get(subject_name='physic')
        self.john.expert_subject.add(physic)
        Subject.objects.create(subject_name='math')
        math = Subject.objects.get(subject_name='math')
        self.john.expert_subject.add(math)

        # John login "Match and Learn" website.
        self.browser.get(self.live_server_url)
        time.sleep(2)
        self.login('john01', 'johnpassword')

        # He clicks his profile link to remove expertise subject.
        john_link = self.browser.find_element_by_link_text('Profile : John')
        john_link.click()
        time.sleep(2)

        # He selects math checkbox to remove it
        table = self.browser.find_element_by_id('expert_subject_table')
        checkbox = table.find_element_by_id('subject_name:2')
        checkbox.click()
        remove_select = self.browser.find_element_by_id("remove_button_id")
        remove_select.send_keys(Keys.ENTER)
        time.sleep(2)

        # the page show lists of his expertise subject.
        self.check_for_row_in_list_table('1: physic')


class MatchTest(LiveServerTestCase):

    def setUp(self):
        # open Firefox.
        self.browser = webdriver.Firefox()
        self.browser.maximize_window()

        # create users for login.
        john_login = User.objects.create_user('john01', 'john@email.com', 'johnpassword')
        john_login.first_name = 'John'
        john_login.last_name = 'Snow'
        john_login.save()
        stefanie_login = User.objects.create_superuser('stefanie01', 'stfanie@email.com', 'stefaniepassword')
        stefanie_login.first_name = 'Stefanie'
        stefanie_login.last_name = 'Walker'
        stefanie_login.save()

        # create users info.
        self.john = Userinfo.objects.create(name='john01', first_name='John', last_name='Snow', age='21',
                                            school='kmutnb')
        self.stefanie = Userinfo.objects.create(name='stefanie01', first_name='Stefanie', last_name='Walker', age='20',
                                                school='kmutnb')

        # John is good at math.
        Subject.objects.create(subject_name='math', subject_keyword='math')
        math = Subject.objects.get(subject_name='math', subject_keyword='math')
        self.john.expert_subject.add(math)
        self.john.save()
        # Stefanie is good at physic.
        Subject.objects.create(subject_name='physic', subject_keyword='physic')
        physic = Subject.objects.get(subject_name='physic', subject_keyword='physic')
        self.stefanie.expert_subject.add(physic)
        self.stefanie.save()

        # create users profile picture.
        Profilepic.objects.create(user=self.john, images='default.png')
        Profilepic.objects.create(user=self.stefanie, images='default.png')

    def tearDown(self):
        self.browser.quit()

    def login(self, username, password):
        username_textbox = self.browser.find_element_by_id("id_username")
        username_textbox.send_keys(username)
        password_textbox = self.browser.find_element_by_id("id_password")
        password_textbox.send_keys(password)
        password_textbox.send_keys(Keys.ENTER)
        time.sleep(2)

    def test_a_can_search_tutor(self):
        # Stefanie login "Match and Learn" website.
        self.browser.get(self.live_server_url)
        self.login('stefanie01', 'stefaniepassword')

        # She wants to find math tutor. She type "math" into subject textbox.
        subject_textbox = self.browser.find_element_by_id('subject_find_id')
        subject_textbox.send_keys('math')
        time.sleep(2)

        # She clicks search button.
        search_btn = self.browser.find_element_by_id('id_search_button')
        search_btn.click()
        time.sleep(10000)

        # She sees John who is good at math.
        john_link = self.browser.find_element_by_id('id_john01').text
        self.assertEqual('John Snow', john_link)
        time.sleep(2)

    def can_accept_request(self):
        # Jesse Lingard search math tutor and find John.
        self.test_a_can_search_tutor()

        # He clicks John profile link.
        john_link = self.browser.find_element_by_id('id_john01')
        self.browser.execute_script("arguments[0].click();", john_link)
        time.sleep(2)

        # He wants John to be a tutor, so he introduce himself in introduce textbox and click "send request"
        introduce = self.browser.find_element_by_id('text_request')
        introduce.send_keys('Hi I am Lingard. I want you to teach me math!')
        send_request = self.browser.find_element_by_name('match')
        time.sleep(2)
        send_request.click()
        time.sleep(2)

        # John login website
        self.browser.get('http://127.0.0.1:8000/login/')
        self.login('john01', 'johnpass')

        # He check student request.
        request_link = self.browser.find_element_by_name('Match request')
        request_link.click()
        time.sleep(2)

        # He sees Lingard request, so he click Lingard profile link.
        lingard_link = self.browser.find_element_by_id('id_lingard14_request')
        lingard_link.click()
        time.sleep(2)

        # He sees introduce message and click "accept" button.
        decision_section = self.browser.find_element_by_id('id_decision_section').text
        self.assertIn('Hi I am Lingard. I want you to teach me math!', decision_section)
        accept_btn = self.browser.find_element_by_name('accept')
        accept_btn.click()
        time.sleep(2)

        # He check that Lingard is his student. He clicks "Students and Tutor list".
        st_link = self.browser.find_element_by_link_text('Students and Tutor list')
        st_link.click()
        time.sleep(2)

        # There is Lingard profile link.
        lingard_link = self.browser.find_element_by_id('id_name_list_lingard14')
        time.sleep(2)

        # Jesse Lingard login "Match and Learn" website.
        self.browser.get('http://127.0.0.1:8000/login/')
        self.login('lingard14', 'jlpassword')

        # He check that John is his tutor. He clicks "Students and Tutor list".
        st_link = self.browser.find_element_by_link_text('Students and Tutor list')
        st_link.click()
        time.sleep(2)

        # There is John profile link.
        john_link = self.browser.find_element_by_id('id_name_list_john01')
        time.sleep(2)


class ChatTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser2 = webdriver.Firefox()

        # create users for login.
        john_login = User.objects.create_user('john01', 'john@email.com', 'johnpassword')
        john_login.first_name = 'John'
        john_login.last_name = 'Snow'
        john_login.save()
        eric_login = User.objects.create_user('eric01', 'eric@email.com', 'ericpassword')
        eric_login.first_name = 'Eric'
        eric_login.last_name = 'Runner'
        eric_login.save()

        # create users info.
        self.john = Userinfo.objects.create(name='john01', first_name='John', last_name='Snow', age='21',
                                            school='kmutnb')
        self.eric = Userinfo.objects.create(name='eric01', first_name='Eric', last_name='Runner', age='22',
                                            school='kmutnb')

        # create users profile picture.
        Profilepic.objects.create(user=self.john, images='default.png')
        Profilepic.objects.create(user=self.eric, images='default.png')

        # John pair with Eric.
        MatchedName.objects.create(myself='john01', match='eric01')
        john_eric = MatchedName.objects.get(myself='john01', match='eric01')
        self.john.match.add(john_eric)
        MatchedName.objects.create(myself='eric01', match='john01')
        eric_john = MatchedName.objects.get(myself='eric01', match='john01')
        self.eric.match.add(eric_john)

    def john_login(self, username, password):
        username_textbox = self.browser.find_element_by_id("id_username")
        username_textbox.send_keys(username)
        password_textbox = self.browser.find_element_by_id("id_password")
        password_textbox.send_keys(password)
        password_textbox.send_keys(Keys.ENTER)
        time.sleep(2)

    def eric_login(self, username, password):
        username_textbox = self.browser2.find_element_by_id("id_username")
        username_textbox.send_keys(username)
        password_textbox = self.browser2.find_element_by_id("id_password")
        password_textbox.send_keys(password)
        password_textbox.send_keys(Keys.ENTER)
        time.sleep(2)

    def tearDown(self):
        self.browser.quit()
        self.browser2.quit()

    def test_can_send_message(self):
        # John wants to chat with Eric so he login and clicks their chat room link.
        self.browser.get('http://127.0.0.1:8000/')
        self.john_login('john01', 'johnpass')

        # Eric wants to chat with John so he login and clicks their chat room link.
        self.browser2.get('http://127.0.0.1:8000/')
        self.eric_login('eric01', 'erpassword')

        # They go to chat room.
        self.browser.get('http://127.0.0.1:8000/chat/eric01_john01/')
        self.browser2.get('http://127.0.0.1:8000/chat/eric01_john01/')

        # John notices the chat textarea, chat textbox and send button.
        john_chat_right = self.browser.find_element_by_id('chat-log')
        john_chat_left = self.browser.find_element_by_id('chat-log2')
        john_chat_textbox = self.browser.find_element_by_id('chat-message-input')
        john_send = self.browser.find_element_by_id('chat-message-submit')

        # Eric notices the chat textarea
        eric_chat_right = self.browser2.find_element_by_id('chat-log')
        eric_chat_left = self.browser2.find_element_by_id('chat-log2')
        eric_chat_textbox = self.browser2.find_element_by_id('chat-message-input')
        eric_send = self.browser2.find_element_by_id('chat-message-submit')

        # John types message "Hi" and clicks send button.
        john_chat_textbox.send_keys('Hi')
        time.sleep(2)
        john_send.click()
        time.sleep(2)

        # John notices his message is sent in textarea
        self.assertIn(
            'john01 : Hi',
            john_chat_right.get_attribute('value')

        )

        # John types message "I'm John" and clicks send button.
        john_chat_textbox.send_keys("I'm John")
        time.sleep(2)
        john_send.click()
        time.sleep(2)

        # John notices his message is sent in textarea
        self.assertIn(
            'john01 : Hi\n'
            "john01 : I'm John\n",
            john_chat_right.get_attribute('value')
        )

        # Then, Eric notices that John sent message
        self.assertIn(
            'john01 : Hi\n'
            "john01 : I'm John\n",
            eric_chat_left.get_attribute('value')
        )

        # Eric types "Hello" and clicks the send button.
        eric_chat_textbox.send_keys('Hello')
        time.sleep(2)
        eric_send.click()
        time.sleep(2)

        # Eric notices the message was sent.
        self.assertIn(
            "eric01 : Hello",
            eric_chat_right.get_attribute('value')
        )

        # Eric types message "I'm Eric" and clicks the send button.
        eric_chat_textbox.send_keys("I'm Eric")
        time.sleep(2)
        eric_send.click()
        time.sleep(2)

        # Eric notices the message was sent.
        self.assertIn(
            "eric01 : Hello\n"
            "eric01 : I'm Eric\n",
            eric_chat_right.get_attribute('value')
        )
        time.sleep(2)

        # John notices that the message from Eric was arrived.
        self.assertIn(
            "eric01 : Hello\n"
            "eric01 : I'm Eric\n",
            john_chat_left.get_attribute('value')
        )
        time.sleep(2)