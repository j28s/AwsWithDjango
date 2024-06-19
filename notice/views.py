from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import View, ListView, DetailView, FormView, CreateView
from .models import Notice
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from .forms import NoticeWriteForm
import mimetypes
from mimetypes import guess_type
import os
import re
from django.http import HttpResponse, HttpResponseRedirect, Http404
from urllib.parse import quote
import urllib
from django.conf import settings
from django.apps import apps
from .decorators import login_message_required, admin_required

User = apps.get_model('users', 'User')




# 공지사항 리스트 뷰
class NoticeListView(ListView):
    model = Notice
    paginate_by = 15
    template_name = 'notice/notice_list.html'  # DEFAULT : <app_label>/<model_name>_list.html
    context_object_name = 'notice_list'  # DEFAULT : <app_label>_list

    def get_queryset(self):
        search_keyword = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', '')
        notice_list = Notice.objects.order_by('-id')

        if search_keyword:
            if len(search_keyword) > 1:
                if search_type == 'all':
                    search_notice_list = notice_list.filter(
                        Q(title__icontains=search_keyword) | Q(content__icontains=search_keyword) | Q(
                            writer__username__icontains=search_keyword))
                elif search_type == 'title_content':
                    search_notice_list = notice_list.filter(
                        Q(title__icontains=search_keyword) | Q(content__icontains=search_keyword))
                elif search_type == 'title':
                    search_notice_list = notice_list.filter(title__icontains=search_keyword)
                elif search_type == 'content':
                    search_notice_list = notice_list.filter(content__icontains=search_keyword)
                elif search_type == 'writer':
                    search_notice_list = notice_list.filter(writer__user_id__icontains=search_keyword)

                return search_notice_list
            else:
                messages.error(self.request, '검색어는 2글자 이상 입력해주세요.')
        return notice_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        page_numbers_range = 5
        max_index = len(paginator.page_range)

        page = self.request.GET.get('page')
        current_page = int(page) if page else 1

        start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range
        end_index = start_index + page_numbers_range
        if end_index >= max_index:
            end_index = max_index

        page_range = paginator.page_range[start_index:end_index]
        context['page_range'] = page_range

        search_keyword = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', '')
        notice_fixed = Notice.objects.filter(top_fixed=True).order_by('-registered_date')

        if len(search_keyword) > 1:
            context['q'] = search_keyword
        context['type'] = search_type
        context['notice_fixed'] = notice_fixed

        return context


# 공지사항 게시글 보기
# @login_message_required
def notice_detail_view(request, pk):
    notice = get_object_or_404(Notice, pk=pk)


    if request.user == notice.writer:
        notice_auth = True
    else:
        notice_auth = False

    context = {
        'notice': notice,
        'notice_auth': notice_auth,
    }

    return render(request, 'notice/notice_detail.html', context)


# 공지사항 글쓰기
@login_message_required
@admin_required
def notice_write_view(request):
    if request.method == "POST":
        form = NoticeWriteForm(request.POST, request.FILES)

        if form.is_valid():
            notice = form.save(commit=False)
            if request.FILES:
                if 'upload_files' in request.FILES.keys():
                    notice.filename = request.FILES['upload_files'].name
            notice.save()
            return redirect('notice:notice_list')
    else:
        form = NoticeWriteForm()
    return render(request, "notice/notice_write.html", {'form': form})


# 공지사항 게시글 수정
@login_message_required
def notice_edit_view(request, pk):
    notice = Notice.objects.get(id=pk)

    if request.method == "POST":
        if request.user.is_superuser:
            file_change_check = request.POST.get('fileChange', False)
            file_check = request.POST.get('upload_files-clear', False)

            if file_check or file_change_check:
                os.remove(os.path.join(settings.MEDIA_ROOT, notice.upload_files.path))

            form = NoticeWriteForm(request.POST, request.FILES, instance=notice)
            if form.is_valid():
                notice = form.save(commit=False)
                if request.FILES:
                    if 'upload_files' in request.FILES.keys():
                        notice.filename = request.FILES['upload_files'].name
                notice.save()
                messages.success(request, "수정되었습니다.")
                return redirect('/notice/' + str(pk))
    else:
        notice = Notice.objects.get(id=pk)
        if request.user.is_superuser:
            form = NoticeWriteForm(instance=notice)
            context = {
                'form': form,
                'edit': '수정하기',
            }
            if notice.filename and notice.upload_files:
                context['filename'] = notice.filename
                context['file_url'] = notice.upload_files.url
            return render(request, "notice/notice_write.html", context)
        else:
            messages.error(request, "본인 게시글이 아닙니다.")
            return redirect('/notice/' + str(pk))


# 공지사항 게시글 삭제
@login_message_required
def notice_delete_view(request, pk):
    notice = Notice.objects.get(id=pk)
    if request.user.is_superuser:
        notice.delete()
        messages.success(request, "삭제되었습니다.")
        return redirect('/notice/')
    else:
        messages.error(request, "본인 게시글이 아닙니다.")
        return redirect('/notice/' + str(pk))


# 공지사항 게시글 첨부파일 다운로드 한글명 인코딩
@login_message_required
def notice_download_view(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    url = notice.upload_files.url[1:]
    print(type(url))
    print(url)
    file_url = urllib.parse.unquote(url)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            quote_file_url = urllib.parse.quote(notice.filename.encode('utf-8'))
            response = HttpResponse(fh.read(), content_type=mimetypes.guess_type(file_url)[0])
            response['Content-Disposition'] = 'attachment;filename*=UTF-8\'\'%s' % quote_file_url
            return response
        raise Http404

