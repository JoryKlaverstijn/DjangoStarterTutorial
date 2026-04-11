from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "q_list"

    def get_queryset(self):
        past_questions = Question.objects.filter(pub_date__lte=timezone.now())
        return past_questions.order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    q = get_object_or_404(Question, pk=question_id)

    try:
        choice = q.choice_set.get(pk=request.POST["choice"])
    except KeyError, Choice.DoesNotExist:
        context = {
            "question": q,
            "error_message": "You didn't select a choice.",
        }
        return render(request, "polls/detail.html", context)

    choice.votes += 1
    choice.save()

    return HttpResponseRedirect(reverse("polls:results", args=(q.id,)))
