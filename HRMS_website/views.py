from django.http import HttpResponse, JsonResponse
from django.shortcuts import render_to_response, redirect
from django.contrib import auth
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from HRMS.settings import API_BASE_LINK
from utils.mandrill_wrapper import send_mail
from rest_framework.authtoken.models import Token
from datetime import datetime, timedelta, date
from urllib.parse import unquote
import requests, json
# Create your views here.

def get_api_token(request):
    return {'Authorization': 'Token {}'.format((dict(request.COOKIES).get('api_token', '')))}


def login(request):
    args = {}
    args.update(csrf(request))
    if request.POST:
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            try:
                token = Token.objects.create(user=user)
            except Exception:
                token = Token.objects.get(user=user)
            response = redirect('/dashboard/')
            response.set_cookie(key='api_token', value=token.key, expires=datetime.today()+timedelta(days=1))
            return response
        else:
            args['login_error'] = "Username or Password you've entered is incorrect, please try again."
            return render_to_response('auth/login.html', args)

    else:
        return render_to_response('auth/login.html', args)


def logout(request):
    try:
        Token.objects.get(user=auth.get_user(request)).delete()
    except Exception:
        pass
    auth.logout(request)
    response = redirect('/')
    try:
        response.delete_cookie('api_token')
    except Exception:
        pass
    return response


def signup(request):
    args = {}
    args.update(csrf(request))
    if request.POST:
        payload = dict(
            first_name=request.POST.get('first_name',''),
            last_name=request.POST.get('last_name',''),
            username=request.POST.get('username',''),
            email=request.POST.get('email',''),
            password=request.POST.get('password',''),
            retype_password=request.POST.get('retype_password',''),
        )
        user =  requests.post("".join([API_BASE_LINK, 'users/']), data=payload)
        json = user.json()
        if 'url' in json:
            user=auth.authenticate(username=payload['username'], password=payload['password'])
            auth.login(request, user)
            return redirect('/dashboard/')
        else:
            for error in json:
                args[error] = "<br>".join(json[error])
            return render_to_response('auth/register.html', args)

    else:
        return render_to_response('auth/register.html', args)


def landing_page(request):
    args = {}
    args['username'] = auth.get_user(request).username
    return render_to_response('landing/index.html', args)


def base(request):
    args = {}
    args['username'] = auth.get_user(request).username
    return render_to_response('base.html')

@csrf_exempt
def contact_form(request):
    name = request.POST.get('name','')
    email_address = request.POST.get('email','')
    phone = request.POST.get('phone','')
    message = request.POST.get('message','')
    if name == '' or email_address == '' or phone == '' or message == '':
        return HttpResponse(False)
    from email.utils import parseaddr
    if parseaddr(email_address) == ('', ''):
        return HttpResponse(False)
    else:
        send_mail(
            'contact_form_responsive',
            ["HumanResource.M.System@gmail.com"],
            context={
                "name": name,
                "email": email_address,
                "phone": str(phone),
                "message": message.replace("\n", "<br>")
            }
        )
        return HttpResponse(True)


def dashboard(request):
    args = {}
    if isinstance(auth.get_user(request), auth.models.AnonymousUser):
        return redirect("/login/")
    args['username'] = auth.get_user(request).username
    args['full_name'] = "{} {}".format(auth.get_user(request).first_name, auth.get_user(request).last_name)
    user = requests.get(url="".join([API_BASE_LINK, 'users/{}/'.format(auth.get_user(request).id)])).json()
    for project in user['user_projects']:
        project['project_details'] = requests.get(project['project'], headers=get_api_token(request), params={'format': 'json'}).json()
        for issue in project['project_details']['issues']:
            issue['options'] = requests.options(issue['url'], headers=get_api_token(request), params={'format': 'json'}).json()
            issue['assigned_to'] = requests.get(issue['assigned_to'], headers=get_api_token(request), params={'format': 'json'}).json()
            issue['created_by'] = requests.get(issue['created_by'], headers=get_api_token(request), params={'format': 'json'}).json()
    args.update(user)
    return render_to_response('board/dashboard.html', args)


def project(request, project_id):
    args = {}
    if isinstance(auth.get_user(request), auth.models.AnonymousUser):
        return redirect("/login/")
    args['username'] = auth.get_user(request).username
    args['project_id'] = int(project_id)
    args['full_name'] = "{} {}".format(auth.get_user(request).first_name, auth.get_user(request).last_name)
    user = requests.get(url="".join([API_BASE_LINK, 'users/{}/'.format(auth.get_user(request).id)])).json()
    args['team_member_options'] = requests.options(url="".join([API_BASE_LINK, 'project_team/']), headers=get_api_token(request), params={'format': 'json'}).json()
    for project in user['user_projects']:
        project['project_details'] = requests.get(project['project'], headers=get_api_token(request), params={'format': 'json'}).json()
        for project_member in project['project_details']['project_team']:
            project_member['user'] = requests.get(project_member['user'], headers=get_api_token(request), params={'format': 'json'}).json()
        for issue in project['project_details']['issues']:
            issue['options'] = requests.options(issue['url'], headers=get_api_token(request), params={'format': 'json'}).json()
            issue['assigned_to'] = requests.get(issue['assigned_to'], headers=get_api_token(request), params={'format': 'json'}).json()
            issue['created_by'] = requests.get(issue['created_by'], headers=get_api_token(request), params={'format': 'json'}).json()
    args.update(user)
    return render_to_response('board/project.html', args)


@csrf_exempt
def create_issue(request):
    args = {}
    if isinstance(auth.get_user(request), auth.models.AnonymousUser):
        return redirect("/login/")
    args['username'] = auth.get_user(request).username
    args['full_name'] = "{} {}".format(auth.get_user(request).first_name, auth.get_user(request).last_name)
    issue = requests.options("".join([API_BASE_LINK, "issues/"]), headers=get_api_token(request), params={'format': 'json'}).json()
    args.update(issue)
    data=dict()
    if request.method == 'POST':
        headers=get_api_token(request)
        headers['Content-type']='application/json'
        for key in request.POST:
            data[key]=request.POST.get(key, '')
        url = "".join([API_BASE_LINK, 'issues', '/'])
        response = requests.post(url=url, headers=headers, data=json.dumps(data)).json()
        return redirect("/dashboard/")
    return render_to_response('board/forms/create_issue.html', args)


@csrf_exempt
def update_issue(request, issue_id):
    headers=get_api_token(request)
    headers['Content-type']='application/json'
    data = dict()
    if request.method == 'GET':
        params = unquote(request.get_full_path()).split('?')[-1].split('&')
        for param in params:
            param=param.split('=')
            if(len(param)<2):
                return HttpResponse("Incorrect payload!!!")
            data[param[0]]=param[1]
    if request.method == 'POST':
        for key in request.POST:
            data[key]=request.POST.get(key, '')
    url = "".join([API_BASE_LINK, 'issues', '/', issue_id, '/'])
    response = requests.patch(url=url, headers=headers, params=data).json()
    return redirect('/dashboard/')


@csrf_exempt
def update_comment(request, comment_id):
    headers=get_api_token(request)
    headers['Content-type']='application/json'
    data = dict()
    url = "".join([API_BASE_LINK, 'comments', '/', comment_id, '/'])
    if request.method == 'GET':
        params = unquote(request.get_full_path()).split('?')[-1].split('&')
        for param in params:
            param=param.split('=')
            if(len(param)<2):
                return HttpResponse("Incorrect payload!!!")
            data[param[0]]=param[1]
    if request.method == 'POST':
        method = request.POST.get('_method', '')
        if str(method).upper() == 'DELETE':
            requests.delete(url=url, headers=headers)
        elif str(method).upper() == 'PATCH':
            for key in request.POST:
                data[key]=request.POST.get(key, '')
            requests.patch(url=url, headers=headers, params=data).json()
        else:
            url = "".join([API_BASE_LINK, 'comments', '/'])
            for key in request.POST:
                data[key]=request.POST.get(key, '')
            requests.post(url=url, headers=headers, params=data).json()
    return redirect('/dashboard/')


@csrf_exempt
def add_work_log(request):
    headers=get_api_token(request)
    headers['Content-type']='application/json'
    data = dict()
    url = "".join([API_BASE_LINK, 'worklogs', '/',])
    response=dict()
    if request.method == 'POST':
        method = request.POST.get('_method', '')
        if str(method).upper() == 'DELETE':
            requests.delete(url=url, headers=headers)
        elif str(method).upper() == 'PATCH':
            for key in request.POST:
                data[key]=request.POST.get(key, '')
            response = requests.patch(url=url, headers=headers, params=data).json()
        else:
            url = "".join([API_BASE_LINK, 'worklogs', '/'])
            for key in request.POST:
                data[key]=request.POST.get(key, '')
            response = requests.post(url=url, headers=headers, params=data).json()
    return JsonResponse(response)


@csrf_exempt
def project_team(request, member_id):
    headers=get_api_token(request)
    headers['Content-type']='application/json'
    data = dict()
    url = "".join([API_BASE_LINK, 'project_team', '/', member_id, '/',])
    response=dict()
    if request.method == 'POST':
        method = request.POST.get('_method', '')
        if str(method).upper() == 'DELETE':
            requests.delete(url=url, headers=headers)
        elif str(method).upper() == 'PATCH':
            for key in request.POST:
                data[key]=request.POST.get(key, '')
            response = requests.patch(url=url, headers=headers, params=data).json()
        else:
            url = "".join([API_BASE_LINK, 'project_team', '/'])
            for key in request.POST:
                data[key]=request.POST.get(key, '')
            response = requests.post(url=url, headers=headers, params=data).json()
    return JsonResponse(response)

@csrf_exempt
def weekly_report(request):
    headers=get_api_token(request)
    headers['Content-type']='application/json'
    url = "".join([API_BASE_LINK, 'worklogs', '/'])
    if request.method == 'GET':
        args = {}
        if isinstance(auth.get_user(request), auth.models.AnonymousUser):
            return redirect("/login/")
        week = []
        for i in range(0,7):
            week.append(date.today() - timedelta(days=i))
        args['week'] = week
        args['username'] = auth.get_user(request).username
        args['full_name'] = "{} {}".format(auth.get_user(request).first_name, auth.get_user(request).last_name)
        worklogs = requests.get(url=url, headers=get_api_token(request), params={'format': 'json'}).json()
        args['worklog_options'] = requests.options(url=url, headers=get_api_token(request), params={'format': 'json'}).json()
        for worklog in worklogs:
            worklog['issue'] = requests.get(worklog['issue'], headers=get_api_token(request), params={'format': 'json'}).json()
            del worklog['issue']['issue_worklogs']
            del worklog['issue']['issue_comments']
        args['worklogs'] = worklogs
        return render_to_response('board/weekly_report.html', args)
    else:
        return JsonResponse({'error': 'Invalid request'})
