from django.db import models
import datetime
from django.db.models.fields.related import ForeignKey
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.


class Question(models.Model):
    """ A object contains set of questions and choices. """

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('end date')

    def is_published(self):
        """ Check whether the question is published or not.

        Returns:
            bool: Returns True if the question is published.
        """
        if timezone.now() >= self.pub_date:
            return True

    def can_vote(self):
        """ Check whether the question is available
        to be vote or not.

        Returns:
            bool: Returns True if the question can be vote.
        """
        if self.is_published() and timezone.now() < self.end_date:
            return True

    def __str__(self) -> str:
        return self.question_text

    def was_published_recently(self):
        """ Check if the question was published today or not.

        Returns:
            bool: Returns True if the question was published within this day
            , else False.
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

    is_published.admin_order_field = 'pub_date'
    is_published.boolean = True
    is_published.short_description = 'Published recently?'


class Choice(models.Model):
    """ Store choice's object """

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    # votes = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.choice_text

    # we want to be able to write 'choice.votes' in our views
    # and templates to get the number of votes for a Choice.
    # We want the existing code to still work.
    @property
    def votes(self) -> int:
        vote_count = Vote.objects.filter(choice=self).count()
        return vote_count


class Vote(models.Model):
    user = ForeignKey(User,
                      null=False,
                      blank=False,
                      on_delete=models.CASCADE
                      )
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Vote by {self.user.username} for {self.choice.choice_text}"
