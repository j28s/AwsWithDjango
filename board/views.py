from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Question, VoteChoice, UserVote
from .forms import VoteForm

def index(request):
    latest_question_list = Question.objects.order_by('-pk')
    return render(
        request,
        'board/index.html',
        {
            'latest_question_list': latest_question_list,
        }
    )

def detail(request, pk):
    question = get_object_or_404(Question, pk=pk)

    return render(
        request,
        'board/detail.html',
        {
            'question': question,
        }
    )

def vote(request, pk):
    question = get_object_or_404(Question, pk=pk)
    choices = question.votechoice_set.all()
    user_vote = UserVote.objects.filter(user=request.user, choices__question=question).first()

    if request.method == 'POST':
        form = VoteForm(request.POST)

        if form.is_valid():
            selected_choices = form.cleaned_data['choices']

            if user_vote:
                # 기존 투표를 수정
                user_vote.choices.clear()
            else:
                # 새로운 투표 생성
                user_vote = UserVote.objects.create(user=request.user)

            user_vote.choices.add(*selected_choices)

            return HttpResponseRedirect(reverse('board:results', args=(pk,)))
    else:
        # 투표한 경우 해당 선택지들을 미리 체크된 상태로 폼에 전달
        initial_data = {'choices': user_vote.choices.values_list('pk', flat=True)} if user_vote else None
        form = VoteForm(initial=initial_data)

    return render(request, 'board/detail.html', {'question': question, 'form': form, 'choices': choices})

def results(request, pk):
    question = get_object_or_404(Question, pk=pk)
    choices = question.votechoice_set.all()
    return render(request, 'board/results.html', {'question': question, 'choices': choices})


