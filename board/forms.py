from django import forms
from .models import VoteChoice

class VoteForm(forms.Form):
    choices = forms.ModelMultipleChoiceField(
        queryset=VoteChoice.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )