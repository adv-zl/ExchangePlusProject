from django.shortcuts import render, redirect
from django.contrib import auth
from django.http import HttpResponseRedirect
# Create your views here.


# основная странциа с формами и функционалом
def test(request):
	content = {
		'doc': 'test.html',
	}
	return render(request, 'test.html')



# основная странциа с формами и функционалом
def index(request):
	if request.user.is_anonymous():
		return HttpResponseRedirect('/login/')
	content = {
		'doc': 'index.html',
	}
	return render(request, 'base.html', content)


# Форма входа юзера
def login(request):
	if request.POST:
		username = request.POST['username']
		password = request.POST['password']
		user = auth.authenticate(username = username, password = password)
		#print(user.get_all_permissions())
		if user is not None and user.is_active:
			auth.login(request, user)
			return HttpResponseRedirect('/index/')
		else:
			return render(request, 'login.html', {'error': 'Неверный логин или пароль!'})
	return render(request, 'login.html')

def logout(request):
	auth.logout(request)
	return render(request, 'logout.html')

# Форма добавления/изменения данных кассира
def creating_user(request):
	pass