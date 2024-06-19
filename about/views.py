from django.shortcuts import render, redirect

def about_us(request):
    return render(
        request,
        'about/about.html',
    )


# 조직도 보기
def organization_view(request):
    return render(request, 'about/organization_list.html')
