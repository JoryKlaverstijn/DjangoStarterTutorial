import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question


def _create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    q = Question(question_text=question_text, pub_date=time)
    q.save()

    return q


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        r = self.client.get(reverse("polls:index"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "No polls are available.")
        self.assertQuerySetEqual(r.context["q_list"], [])

    def test_past_question(self):
        q1 = _create_question(question_text="Q1", days=-15)
        q2 = _create_question(question_text="Q2", days=-30)

        r = self.client.get(reverse("polls:index"))

        self.assertQuerySetEqual(r.context["q_list"], [q1, q2])

    def test_future_question(self):
        _create_question(question_text="Future question.", days=30)
        r = self.client.get(reverse("polls:index"))

        self.assertContains(r, "No polls are available.")
        self.assertQuerySetEqual(r.context["q_list"], [])


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        q = _create_question(question_text="Future question.", days=30)

        url = reverse("polls:detail", args=(q.id,))
        r = self.client.get(url)

        self.assertEqual(r.status_code, 404)

    def test_past_question(self):
        q1 = _create_question(question_text="Past question 1.", days=-30)
        q2 = _create_question(question_text="Past question 2.", days=-15)

        url = reverse("polls:detail", args=(q1.id,))

        r = self.client.get(url)

        self.assertContains(r, q1.question_text)
        self.assertNotContains(r, q2.question_text)
