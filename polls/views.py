# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Choice, Question, Vote
import logging


class IndexView(generic.ListView):
    """ Display latest 5 polls """

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now())\
            .order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    """ Display all poll's choices """

    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_vote = None
        user = self.request.user
        if user.is_authenticated:
            try:
                previous_vote = Vote.objects.\
                    get(user=user, choice__question=context["question"])
            except Vote.DoesNotExist:
                pass

        if previous_vote:
            context["previous_vote"] = previous_vote
        return context


class ResultsView(generic.DetailView):
    """ Display vote results """

    model = Question
    template_name = 'polls/results.html'


@login_required(login_url='/accounts/login/')
def vote(request, question_id):
    """ Apply a vote to the selected question's object. """

    question = get_object_or_404(Question, pk=question_id)
    try:
        choice_id = request.POST['choice']
        selected_choice = question.choice_set.get(pk=choice_id)
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        # Record the vote
        user = request.user
        vote = get_vote_for_user(user, question)
        # case 1: user has not voted for this poll question yet
        #         Creat a new Vote object
        if not vote:
            vote = Vote(user=user, choice=selected_choice)
        else:
            # cases 2: user has already voted
            #          Modify the existing vote and save it
            vote.choice = selected_choice
        logger = logging.getLogger("polls")
        logger.info(f"{user} votes for {vote.choice} in {question}.")
        vote.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results',
                                            args=(question.id,)))


def get_vote_for_user(user, poll_question):
    """Find and return an existing vote for a user on a poll question.

    Returns:
        The users Vote or None if no vote for this poll_question
    """
    try:
        vote = Vote.objects.filter(user=user)\
            .filter(choice__question=poll_question)
        if vote.count() == 0:
            return None
        else:
            return vote[0]
    except Vote.DoesNotExist:
        return None
