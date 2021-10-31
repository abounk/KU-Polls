from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from polls.models import Question
import datetime
from django.utils import timezone
from html import escape


class VotingTest(TestCase):
    """Test voting."""

    def setUp(self):
        now = timezone.now()
        end_date = now + datetime.timedelta(days=1)
        self.question = Question.objects.create(question_text="question 1",
                                                pub_date=now,
                                                end_date=end_date
                                                )
        self.choice1 = self.question.choice_set.create(choice_text="choice 1")
        self.choice2 = self.question.choice_set.create(choice_text="choice 2")

        self.vote_url = reverse("polls:vote", args=[self.question.id])

        self.username = "test_username"
        self.password = "test_password"
        self.user = User.objects.create_user(username=self.username,
                                             password=self.password,
                                             )

    def login(self):
        self.client.login(username=self.username,
                          password=self.password
                          )

    def test_vote_without_logging_in(self):
        """Voting when not logged in will not be counted as a vote."""
        self.client.post(self.vote_url,
                         data={"choice": self.choice1.id}
                         )
        self.assertEqual(self.choice1.votes, 0)

    def test_redirect_when_not_authorized(self):
        """
        Voting with out logging in will redirect
        user to login page.
        """
        login_page = f"{reverse('login')}?next={self.vote_url}"
        response = self.client.post(
            self.vote_url, data={"choice": self.choice1.id})
        self.assertRedirects(response, login_page)

    def test_vote(self):
        """Normal vote."""
        self.login()
        self.client.post(self.vote_url, data={"choice": self.choice1.id})
        self.assertEqual(self.choice1.votes, 1)

    def test_vote_same_choice(self):
        """Vote same choice will not increase voting result."""
        self.login()
        for _ in range(5):
            self.client.post(self.vote_url, data={"choice": self.choice1.id})
        self.assertEqual(self.choice1.votes, 1)

    def test_votting_with_invalid_choice_id(self):
        """Voting with invalid choice's id"""
        self.login()
        error_massage = "You didn't select a choice."
        response = self.client.post(self.vote_url, data={"choice": 0})
        self.assertContains(response, escape(error_massage))

    def test_change_vote(self):
        """
        Voting different choice in the same question
        will replace the old one.
        """
        self.login()
        self.client.post(self.vote_url, data={"choice": self.choice1.id})
        self.assertEqual(self.choice1.votes, 1)

        self.client.post(self.vote_url, data={"choice": self.choice2.id})
        self.assertEqual(self.choice2.votes, 1)
        self.assertEqual(self.choice1.votes, 0)
