from django.contrib.auth.models import User
from django.db import models

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.question_text}'

class VoteChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.choice_text}'

class UserVote(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    choices = models.ManyToManyField(VoteChoice)

    def __str__(self):
        return f"{self.user.username}\'s votes" if self.user else 'Anonymous votes'
