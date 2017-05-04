from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from django.http import HttpResponseRedirect
from .models import OrdinaryCashier, ExchangeActions, User
import json
import datetime
import re


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
		person = OrdinaryCashier.objects.filter(user__username = request.user.username)
		person = person[0]
		exchange_rate = json.loads(person.exchange_rate)

	content = {
		'doc': 'index.html',

		'user_menu': 'elements/user_menu.html',
		'exchange_rate': 'elements/exchange_rate.html',
		'user_create': 'elements/user_create.html',
		'new_operation': 'elements/new_operation.html',
		'transaction_table': 'elements/transaction_table.html',

		'encashment': 'forms/encashment_form.html',
		'support_form': 'forms/support_form.html',
		'exchange_form': 'forms/exchange_change_form.html',

		'role': role,
		'users': users_list,
		'user_inform': person,
		'exchange_rate_data': exchange_rate,
		'surname': request.session['0'],
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
			person = OrdinaryCashier.objects.filter(user__username = username)
			# Перенаправляем на страницу кассы
			return HttpResponseRedirect('/view-cashbox/{0}'.format(person[0].id))
		else:
			return render(request, 'login.html', {'error': 'Неверный логин или пароль!'})
	return render(request, 'login.html')


def logout(request):
	auth.logout(request)
	request.session = ''
	return render(request, 'logout.html')


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
		'surname': request.session['0'],
	}
	return render(request, 'base.html', content)


# Страница создания новой кассы
def create(request):
	# Проверка прав доступа
	if not request.user.has_perm('ExchangeHelper.delete_exchangeactions'):
		return HttpResponseRedirect('/index/')
	if request.user.is_anonymous():
		return HttpResponseRedirect('/login/')
	# Получение списка всех касс
	users_list = OrdinaryCashier.objects.all()
	error = ''

	# Обработка форм
	if request.POST:
		user, created = User.objects.get_or_create(username = request.POST['username'],
													password = request.POST['password'])
		if not created:
			error = 'Пользователь с таким именем уже существует.'
		else:
			# Создаём нового юзера
			user.save()
			# Считываем описание кассы
			cashier_description_full = request.POST['description_full']
			cashier_description_short = request.POST['description_short']
			# Считываем курсы валют
			exchange_rate = get_exchange_rate(request)
			# Сохраняем данные
			OrdinaryCashier.objects.create(
					user = user,
					cashier_description_full = cashier_description_full,
					cashier_description_short = cashier_description_short,
					exchange_rate = exchange_rate
			).save()

			return HttpResponseRedirect('/index/')

	content = {
		'doc': 'create_new_cashbox.html',
		'user_create': 'elements/user_create.html',

		'role': True,
		'error': error,
		'users': users_list,
		'surname': request.session['0'],
	}
	return render(request, 'base.html', content)


# Страница для просмотра касс
def view_cashbox(request, id):
	role = True
	# Проверка прав доступа
	if not request.user.has_perm('ExchangeHelper.delete_exchangeactions'):
		role = False
	if request.user.is_anonymous():
		return HttpResponseRedirect('/login/')

	# Список событий
	actions = []
	# Контент страницы
	content = {
		'doc': 'view-cashbox.html',
		'user_menu': 'elements/user_menu.html',
		'new_operation': 'elements/new_operation.html',
		'exchange_rate': 'elements/exchange_rate.html',
		'transaction_table': 'elements/transaction_table.html',

		'encashment': 'forms/encashment_form.html',
		'support_form': 'forms/support_form.html',
		'exchange_form': 'forms/exchange_change_form.html',

		'id': id,
		'role': role,
		'surname': request.session['0'],
	}
	rest_money_data = None
	# Получение данных определённой кассы
	certain_cashbox = get_object_or_404(OrdinaryCashier, id = id)
	content['user_inform']= certain_cashbox
	# Получение данных транзакций и сумм валют определённой кассы
	transaction_table_data = ExchangeActions.objects.filter(person_data__id = id,
															operation_date = datetime.date.today())

	content['rest_money_data'] = get_rest_money(rest_money_data, id)

	if transaction_table_data:
		for action in transaction_table_data:
			actions.append({
				"action": action,
				# Получение данных о балансе
				"money_balance_data": json.loads(str(action.money_balance)),
				# Получение данных о операциях
				"actions_data": json.loads(str(action.action)),
			})
		content['actions'] = actions
	# Курсы валют
	content['exchange_rate_data'] = json.loads(certain_cashbox.exchange_rate)

	# Обработка форм
	if request.POST:
		# Вносим изменения в курсы валют
		if 'exchange_rate_save' in request.POST:
			certain_cashbox.exchange_rate = get_exchange_rate(request)
			certain_cashbox.save()
			return HttpResponseRedirect('/view-cashbox/{0}'.format(id))
		# Добавляем операцию
		else:
			count_result_of_action(request, id)

	return render(request, 'base.html', content)


# Страница для изменения кассы
def edit_cashbox(request, id):
	if request.user.is_anonymous():
		return HttpResponseRedirect('/login/')
	# Проверка прав доступа
	if not request.user.has_perm('ExchangeHelper.delete_exchangeactions'):
		return HttpResponseRedirect('/index/')

	# Получение определённой кассы
	certain_cashbox = get_object_or_404(OrdinaryCashier, id = id)
	exchange_rate = json.loads(certain_cashbox.exchange_rate)

	if request.POST:
		# Считываем курсы валют
		exchange_rate = get_exchange_rate(request)
		# Сохраняем данные
		certain_cashbox.user.username = request.POST['username']
		if request.POST['password']:
			certain_cashbox.user.password = request.POST['password']
		certain_cashbox.cashier_description_full = request.POST['description_full']
		certain_cashbox.cashier_description_short = request.POST['description_short']
		certain_cashbox.exchange_rate = exchange_rate
		certain_cashbox.save()

		return HttpResponseRedirect('/index/')

	content = {
		'doc': 'edit_cashbox.html',
		'user_create': 'elements/user_create.html',

		'cashbox_data': certain_cashbox,
		'exchange_rate_data': exchange_rate,
		'surname': request.session['0'],
		'role': True,
	}
	return render(request, 'base.html', content)


# Получаем значения курсов валют со страницы
def get_exchange_rate(request):
	return json.dumps({
				"usd_buy": request.POST['usd_buy'], "usd_sell": request.POST['usd_sell'],
				"eur_buy": request.POST['eur_buy'], "eur_sell": request.POST['eur_sell'],
				"rub_buy": request.POST['rub_buy'], "rub_sell": request.POST['rub_sell'],
				"cad_buy": request.POST['cad_buy'], "cad_sell": request.POST['cad_sell'],
				"chf_buy": request.POST['chf_buy'], "chf_sell": request.POST['chf_sell'],
				"gbp_buy": request.POST['gbp_buy'], "gbp_sell": request.POST['gbp_sell'],
				"pln_buy": request.POST['pln_buy'], "pln_sell": request.POST['pln_sell'],
			})


# Обработчик действий администратора
def count_result_of_action(request, cashbox_id):
	result = {}
	# Выделяем денежную поддержку кассе
	if 'support_btn' in request.POST:
		result["action"] = 'Increase'
		result["changes"] = {request.POST['currency']: request.POST['support_summ']}
		result["comment"] = re.sub(r'\s+', ' ', request.POST['comment'])
		print(result)
	# Отправляем инкассацию
	elif 'encashment_btn' in request.POST:
		result["action"] = 'Encashment'
		result["changes"] = {request.POST['currency']: request.POST['encashment_summ']}
		result["comment"] = re.sub(r'\s+', ' ', request.POST['comment'])
		print(result)
	elif 'new_operation' in request.POST:
		result["action"] = 'Exchange'
		print('Новая операция')


# Получение информации о балансе за прошлый день
def get_rest_money(rest_money_data, id):
	date = datetime.date.today()
	# Если данных за сегодня нет - получаем данные за вчерашний день, о сумме валюте
	while not rest_money_data:
		date = date.replace(day = date.day - 1)
		rest_money_data = ExchangeActions.objects.filter(person_data__id = id,
														operation_date = date)
	# Получение информации о балансе за прошлый день
	rest_money_data = json.loads(str(rest_money_data[0].money_balance))
	rest_money_data['date'] = date
	return rest_money_data