from django.contrib import admin
from .models import Question, VoteChoice, UserVote

admin.site.register(Question)
admin.site.register(VoteChoice)
admin.site.register(UserVote)