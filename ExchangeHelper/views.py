from django.shortcuts import render, redirect
from django.contrib import auth
from django.http import HttpResponseRedirect
from .models import OrdinaryCashier, ExchangeActions, User
# Create your views here.


# основная странциа с формами и функционалом
def index(request):
	users = OrdinaryCashier.objects.all()
	person = OrdinaryCashier.objects.filter(user__username = request.user.username)
	if person:
		person = person[0]
	else:
		person = 'Администратор'
	role = False
	alert = False
	if request.user.has_perm('ExchangeHelper.delete_exchangeactions'):
		role = True
	if request.user.is_anonymous():
		return HttpResponseRedirect('/login/')
	content = {
		'doc': 'index.html',
		'role': role,
		'user_menu': 'user_menu.html',
		'alert': alert,
		'users': users,
		'person': person
	}
	return render(request, 'base.html', content)


# Форма входа юзера
def login(request):
	if request.POST:
		username = request.POST['username']
		password = request.POST['password']
		user = auth.authenticate(username = username, password = password)
		if user is not None and user.is_active:
			#print(user.get_group_permissions())
			auth.login(request, user)
			return HttpResponseRedirect('/index/')
		else:
			return render(request, 'login.html', {'error': 'Неверный логин или пароль!'})
	return render(request, 'login.html')

def logout(request):
	auth.logout(request)
	return render(request, 'logout.html')

# Форма добавления/изменения данных кассира
def create_user(request):
	pass