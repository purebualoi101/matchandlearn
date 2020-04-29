from django.test import TestCase
from tinderforeduapp.models import Userinfo, MatchedName, Comment, Profilepic
from django.contrib.auth.models import User
from datetime import datetime


# Create your tests here.

class ReviewTest(TestCase):

    def setUp(self):
        # create users for login.
        User.objects.create_user('john01', 'john@email.com', 'johnpassword')
        User.objects.create_user('stefanie01', 'stfanie@email.com', 'stefaniepassword')
        User.objects.create_user('eric01', 'eric@email.com', 'ericpassword')

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

        # create current time string.
        now = datetime.now()
        self.dt_string = now.strftime("%B %d, %Y, %I:%M %p")

    def test_send_review(self):
        # login as Stefanie.
        self.client.login(username='stefanie01', password='stefaniepassword')

        # Stefanie sends comment to John.
        self.client.post('/' + str(self.john.id) + '/watch_profile', {'comment': 'very good', 'star': '5',
                                                                      'send_review': 'send_review'})

        # check that comment is sent.
        all_comment = Comment.objects.all()
        self.assertEqual(all_comment.count(), 1)
        first_comment = all_comment[0]
        self.assertEqual(first_comment.star, '5')
        self.assertEqual(first_comment.comment, 'very good')

        # login as Eric.
        self.client.login(username='eric01', password='ericpassword')

        # Eric sends comment to John.
        self.client.post('/' + str(self.john.id) + '/watch_profile', {'comment': 'so bad', 'star': '1',
                                                                      'send_review': 'send_review'})

        # check that comment is sent.
        all_comment = Comment.objects.all()
        self.assertEqual(all_comment.count(), 2)
        second_comment = all_comment[1]
        self.assertEqual(second_comment.star, '1')
        self.assertEqual(second_comment.comment, 'so bad')

    def test_remove_review(self):
        # login as Stefanie.
        self.client.login(username='stefanie01', password='stefaniepassword')

        # create review ( Stefanie send review to John ).
        Comment.objects.create(post=self.john, name='stefanie01', comment='very good', star='5')

        # Stefanie remove review.
        self.client.post('/' + str(self.john.id) + '/watch_profile', {'remove_review': 'remove_review'})

        # check that comment is removed.
        all_comment = Comment.objects.all()
        self.assertEqual(all_comment.count(), 0)

    def test_edit_review(self):
        # login as Stefanie.
        self.client.login(username='stefanie01', password='stefaniepassword')

        # create review ( Stefanie send review to John ).
        Comment.objects.create(post=self.john, name='stefanie01', comment='very good', star='5')

        # Stefanie edits review.
        self.client.post('/' + str(self.john.id) + '/watch_profile', {'comment': 'so bad', 'star': '1',
                                                                      'send_review': 'send_review'})

        # check that comment is edited.
        all_comment = Comment.objects.all()
        self.assertEqual(all_comment.count(), 1)
        first_comment = all_comment[0]
        self.assertEqual(first_comment.star, '1')
        self.assertEqual(first_comment.comment, 'so bad' + "  (edited on : " + self.dt_string + ')')
