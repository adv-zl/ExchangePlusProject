from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from django.http import HttpResponseRedirect
from .models import OrdinaryCashier, ExchangeActions, User
import json
# Create your views here.


# основная странциа с формами и функционалом
def index(request):
	if request.user.is_anonymous():
		return HttpResponseRedirect('/login/')

	# Список всех касс
	users_list = OrdinaryCashier.objects.all()
	# Таблица курсов валют
	exchange_rate = ''
	# ФИО юзера которое он ввёл при входе
	person = ''
	# Администратор или нет
	role = False
	if request.user.has_perm('ExchangeHelper.delete_exchangeactions'):
		role = True
	else:
		person = (OrdinaryCashier.objects.filter(user__username =
												request.user.username))[0]
		exchange_rate = json.loads(person.exchange_rate)

	content = {
		'doc': 'index.html',

		'user_menu': 'elements/user_menu.html',
		'exchange_rate': 'elements/exchange_rate.html',
		'user_create': 'elements/user_create.html',

		'new_operation_form': 'forms/new_operation_form.html',
		'encashment': 'forms/encashment_form.html',
		'support_form': 'forms/support_form.html',
		'exchange_form': 'forms/exchange_change_form.html',

		'role': role,
		'users': users_list,
		'user_inform': person,
		'exchange_rate_data': exchange_rate,
		'person': request.session['0'],
	}
	return render(request, 'base.html', content)


# Форма входа юзера
def login(request):
	if request.POST:
		username = request.POST['username']
		password = request.POST['password']
		# Сохроняем ФИО залогиненного юзера
		request.session[0] = request.POST['surname']
		user = auth.authenticate(username = username, password = password)
		if user is not None and user.is_active:
			auth.login(request, user)
			return HttpResponseRedirect('/index/')
		else:
			return render(request, 'login.html', {'error': 'Неверный логин или пароль!'})
	return render(request, 'login.html')


def logout(request):
	auth.logout(request)
	request.session = ''
	return render(request, 'logout.html')


# Форма добавления/изменения данных кассы
def edit_cashbox(request, id):
	# Проверка прав доступа
	if not request.user.has_perm('ExchangeHelper.delete_exchangeactions'):
		return HttpResponseRedirect('/index/')
	if request.user.is_anonymous():
		return HttpResponseRedirect('/login/')

	# Получение определённой кассы
	certain_cashbox = get_object_or_404(OrdinaryCashier, id = id)
	person = (OrdinaryCashier.objects.filter(cashier_description_short =
											certain_cashbox))[0]
	exchange_rate = json.loads(person.exchange_rate)

	# Обработка форм
	if request.POST:
		# Выделяем денежную поддержку кассе
		if 'support_btn' in request.POST:
			print('Приша поддержка деньгами')
		# Отправляем инкассацию
		elif 'encashment_btn' in request.POST:
			print(request.POST)
		# Вносим изменения в курсы валют
		elif 'exchange_rate_save' in request.POST:
			certain_cashbox.exchange_rate =\
			json.dumps({
				"usd_buy": request.POST['usd_buy'], "usd_sell": request.POST['usd_sell'],
				"eur_buy": request.POST['eur_buy'], "eur_sell": request.POST['eur_sell'],
				"rub_buy": request.POST['rub_buy'], "rub_sell": request.POST['rub_sell'],
				"cad_buy": request.POST['cad_buy'], "cad_sell": request.POST['cad_sell'],
				"chf_buy": request.POST['chf_buy'], "chf_sell": request.POST['chf_sell'],
				"gbp_buy": request.POST['gbp_buy'], "gbp_sell": request.POST['gbp_sell'],
				"pln_buy": request.POST['pln_buy'], "pln_sell": request.POST['pln_sell'],
			})
			certain_cashbox.save()
			return HttpResponseRedirect('/view-cashbox/{0}'.format(id))
		# Добавляем операцию
		elif 'new_operation' in request.POST:
			print('Новая операция')
		else:
			print('Что-то другое')

	content = {
		'doc': 'view-cashbox.html',
		'role': True,
		'user_menu': 'elements/user_menu.html',
		'exchange_rate': 'elements/exchange_rate.html',
		'user_inform': person,
		'exchange_rate_data': exchange_rate,
		'person': request.session['0'],
		'new_operation_form': 'forms/new_operation_form.html',
		'encashment': 'forms/encashment_form.html',
		'support_form': 'forms/support_form.html',
		'exchange_form': 'forms/exchange_change_form.html',
	}
	return render(request, 'base.html', content)


# Личный кабинет юзера
def private(request):
	# Проверка прав доступа
	if not request.user.has_perm('ExchangeHelper.delete_exchangeactions'):
		return HttpResponseRedirect('/index/')
	if request.user.is_anonymous():
		return HttpResponseRedirect('/login/')

	# Обработка форм
	if request.POST:
		print(request.POST)

	content = {
		'doc': 'profile.html',
		'user_create': 'elements/user_create.html',
		'role': True,
		'person': request.session['0'],
	}
	return render(request, 'base.html', content)


# Страница создания новой кассы
def create(request):
	# Проверка прав доступа
	if not request.user.has_perm('ExchangeHelper.delete_exchangeactions'):
		return HttpResponseRedirect('/index/')
	if request.user.is_anonymous():
		return HttpResponseRedirect('/login/')

	# Обработка форм
	if request.POST:
		print(request.POST)

	content = {
		'doc': 'profile.html',
		'user_create': 'elements/user_create.html',
		'role': True,
		'person': request.session['0'],
	}
	return render(request, 'base.html', content)