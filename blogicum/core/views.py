from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def internet_server_error(request):
    return render(request, 'pages/500.html', status=500)


def access_denied(request, exception):
    return render(request, 'pages/403.html', status=403)
