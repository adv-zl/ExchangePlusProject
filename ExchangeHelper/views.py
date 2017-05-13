from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from django.http import HttpResponseRedirect
from .models import AdministratorCashCosts, OrdinaryCashier, ExchangeActions, User
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
	admin_messages = ''
	if request.user.has_perm('ExchangeHelper.delete_exchangeactions'):
		role = True
		# ПОлучение списка всех записок
		admin_messages = len(AdministratorCashCosts.objects.all())
	else:
		person = OrdinaryCashier.objects.filter(user__username = request.user.username)
		person = person[0]
		exchange_rate = json.loads(person.exchange_rate)

	content = {
		'doc': 'index.html',

		'role': role,
		'users': users_list,
		'user_inform': person,
		'exchange_rate_data': exchange_rate,
		'surname': request.session['0'],
		'admin_messages': admin_messages,
	}
	return render(request, 'base.html', content)


# Главная страница с кратким описание проекта
def home(request):
	content = {
		'doc': 'home.html',
	}
	if not request.user.is_anonymous():
		content['surname'] = 'Аноним'
		if request.session['0']:
			content['surname'] = request.session['0']
		if request.user.has_perm('ExchangeHelper.delete_exchangeactions'):
			content['role'] = True

	return render(request, 'base.html', content)


# Главная страница с кратким описание проекта
def wiki(request):
	content = {
		'doc': 'wiki.html',
	}
	if not request.user.is_anonymous():
		content['surname'] = 'Аноним'
		if request.session['0']:
			content['surname'] = request.session['0']
		if request.user.has_perm('ExchangeHelper.delete_exchangeactions'):
			content['role'] = True

	return render(request, 'base.html', content)


# Форма входа юзера
def login(request):
	content = {
		'doc': 'login.html',
	}
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
			content['error'] = 'Неверный логин или пароль!'
			return render(request, 'base.html', content)
	return render(request, 'base.html', content)


def logout(request):
	auth.logout(request)
	request.session = ''
	content = {
		'doc': 'logout.html',
	}
	return render(request, 'base.html', content)


# Личный кабинет юзера
def private(request):
	# Проверка прав доступа
	if not request.user.has_perm('ExchangeHelper.delete_exchangeactions'):
		return HttpResponseRedirect('/index/')
	if request.user.is_anonymous():
		return HttpResponseRedirect('/login/')
	# ПОлучение списка всех записок
	admin_messages = len(AdministratorCashCosts.objects.all())
	# Получение списка записок/трат
	waste_list = AdministratorCashCosts.objects.all()
	if not waste_list:
		waste_list = None

	# Обработка форм
	if request.POST:
		if 'wasting_money_btn' in request.POST:
			AdministratorCashCosts(
					waste_cashbox = OrdinaryCashier.objects.get(user__username = request.user.username),
					waste_author = request.session['0'],
					waste_reason = request.POST['wasting_reason'],
					waste_summ = request.POST['wasting_summ'],
					waste_currency = request.POST['currency'],
					waste_comment = re.sub(r'\s+', ' ', request.POST['comment']),
					waste_date = datetime.date.today(),
					waste_time = datetime.datetime.now().strftime("%H:%M:%S"),
			).save()
			return HttpResponseRedirect('/private/')

	content = {
		'doc': 'profile.html',

		'role': True,
		'waste_list': waste_list,
		'surname': request.session['0'],
		'admin_messages': admin_messages
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
		user, created = User.objects.get_or_create(username = request.POST['username'])
		if not created:
			error = 'Пользователь с таким именем уже существует.'
		else:
			date = datetime.date.today()
			# Создаём нового юзера
			user.set_password(request.POST['password'])
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
			# Создаём операцию по выделению денег новой кассе
			ExchangeActions.objects.create(
					operation_date = date.replace(day = date.day - 1),
					operation_time = datetime.datetime.now().strftime("%H:%M:%S"),
					person_data = get_object_or_404(OrdinaryCashier, user = user),
					person_surname = request.session['0'],
					money_balance = json.dumps({
												"uah": 0,
												"usd": 0,
												"eur": 0,
												"rub": 0,
												"cad": 0,
												"chf": 0,
												"gbp": 0,
												"pln": 0
											}),
					action = json.dumps({
										"action": "Новая касса",
										"changes": {
													"uah": 0,
													"usd": 0,
													"eur": 0,
													"rub": 0,
													"cad": 0,
													"chf": 0,
													"gbp": 0,
													"pln": 0
													},
										"comment": "Нчальный баланс"
									})
			).save()

			return HttpResponseRedirect('/index/')

	content = {
		'doc': 'create_new_cashbox.html',

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
	# ПОлучение списка всех записок
	admin_messages = len(AdministratorCashCosts.objects.all())

	# Список событий
	actions = []
	# Контент страницы
	content = {
		'doc': 'view-cashbox.html',

		'id': id,
		'role': role,
		'admin_messages': admin_messages,
		'surname': request.session['0'],
	}
	rest_money_data = None
	# Получение данных определённой кассы
	certain_cashbox = get_object_or_404(OrdinaryCashier, id = id)
	content['user_inform'] = certain_cashbox
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
		# Вывод информации об операциях за определённую дату
		elif 'certain_date_info' in request.POST:
			# TODO выводить операции по определённой дате
			print('GET DATA INFO')
			print(request.POST)
		# Обработка формы создания записки
		elif 'wasting_money_btn' in request.POST:
			AdministratorCashCosts(
					waste_cashbox = get_object_or_404(OrdinaryCashier, id = id),
					waste_author = request.session['0'],
					waste_reason = request.POST['wasting_reason'],
					waste_summ = request.POST['wasting_summ'],
					waste_currency = request.POST['currency'],
					waste_comment = re.sub(r'\s+', ' ', request.POST['comment']),
					waste_date = datetime.date.today(),
					waste_time = datetime.datetime.now().strftime("%H:%M:%S"),
			).save()
			return HttpResponseRedirect('/view-cashbox/{0}'.format(id))
		# Обработка остальных операций
		else:
			count_result_of_action(request, id)
			return HttpResponseRedirect('/view-cashbox/{0}'.format(id))

	return render(request, 'base.html', content)


# Страница для изменения кассы
def edit_cashbox(request, id):
	# TODO Внести изменения в редактирования пароля касс т.к. не изменяет его
	if request.user.is_anonymous():
		return HttpResponseRedirect('/login/')
	# Проверка прав доступа
	if not request.user.has_perm('ExchangeHelper.delete_exchangeactions'):
		return HttpResponseRedirect('/index/')
	# ПОлучение списка всех записок
	admin_messages = len(AdministratorCashCosts.objects.all())
	# Получение определённой кассы
	certain_cashbox = get_object_or_404(OrdinaryCashier, id = id)
	exchange_rate = json.loads(certain_cashbox.exchange_rate)

	if request.POST:
		# Считываем курсы валют
		exchange_rate = get_exchange_rate(request)
		# Сохраняем данные
		certain_cashbox.user.username = request.POST['username']
		if request.POST['password']:
			certain_cashbox.user.set_password(request.POST['password'])
		certain_cashbox.cashier_description_full = request.POST['description_full']
		certain_cashbox.cashier_description_short = request.POST['description_short']
		certain_cashbox.exchange_rate = exchange_rate
		certain_cashbox.save()

		return HttpResponseRedirect('/index/')

	content = {
		'doc': 'edit_cashbox.html',

		'cashbox_data': certain_cashbox,
		'exchange_rate_data': exchange_rate,
		'surname': request.session['0'],
		'role': True,
		'admin_messages': admin_messages,
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


# Обработчик действий выдачи средств/инкассации и операций обмена
def count_result_of_action(request, cashbox_id):
	result = {}
	# Выделяем денежную поддержку кассе
	if 'support_btn' in request.POST:
		result["action"] = 'Increase'
		result["changes"] = {request.POST['currency']: request.POST['support_summ']}
		result["comment"] = re.sub(r'\s+', ' ', request.POST['comment'])
		# Производим изменение баланса денег
		money_balance = change_money_balance(result, cashbox_id)
		cashier = get_object_or_404(OrdinaryCashier, id = cashbox_id)
		ExchangeActions.objects.create(
				operation_date = datetime.date.today(),
				operation_time = datetime.datetime.now().strftime("%H:%M:%S"),
				person_data = cashier,
				person_surname = request.session['0'],
				money_balance = json.dumps(money_balance),
				action = json.dumps(result)
		).save()
	# Отправляем инкассацию
	elif 'encashment_btn' in request.POST:
		result["action"] = 'Encashment'
		result["changes"] = {request.POST['currency']: '-'+request.POST['encashment_summ']}
		result["comment"] = re.sub(r'\s+', ' ', request.POST['comment'])
		# Производим изменение баланса денег
		money_balance = change_money_balance(result, cashbox_id)
		cashier = get_object_or_404(OrdinaryCashier, id = cashbox_id)
		ExchangeActions.objects.create(
				operation_date = datetime.date.today(),
				operation_time = datetime.datetime.now().strftime("%H:%M:%S"),
				person_data = cashier,
				person_surname = request.session['0'],
				money_balance = json.dumps(money_balance),
				action = json.dumps(result)
		).save()
	# Новая операция
	elif 'new_operation' in request.POST:
		result["action"] = 'Exchange'
		print('EXCHANGE NEW OPERATION')
		print(request.POST)
	# Удаление операции
	elif 'delete_operation' in request.POST:
		# TODO удаление операций начисления и обмена валют
		# Получение последнего актуального баланса денег в кассе
		money_balance = json.loads(ExchangeActions.objects.filter(
														person_data__id = cashbox_id
														).order_by('-id')[0].money_balance
									)
		# Получение данных об операции которую хотим удалить, по id
		deleted_action = get_object_or_404(ExchangeActions,
											id = int(request.POST['delete_operation']))
		# Если была инкассация
		if json.loads(deleted_action.action)['action'] == 'Encashment':
			# парсинг результата действия
			for key in json.loads(deleted_action.action)["changes"].keys():
				# Запись информации о валюте/сумме которую изменяем
				result["changes"] = {
					key: -(float(json.loads(deleted_action.action)['changes'][key])),
				}
				money_balance[key] = float(money_balance[key]) - float(json.loads(deleted_action.action)['changes'][key])
			result["action"] = 'Increase'
			result["comment"] = "Удаление операции №{0} от {1}".format(
																		deleted_action.id,
																		deleted_action.operation_time
																		)
			# Получение денежного баланса
			money_balance = change_money_balance(result, cashbox_id)
			# Создание новой операции
			ExchangeActions(
					operation_date = datetime.date.today(),
					operation_time = datetime.datetime.now().strftime("%H:%M:%S"),
					person_data = get_object_or_404(OrdinaryCashier, id = cashbox_id),
					person_surname = request.session['0'],
					money_balance = json.dumps(money_balance),
					action = json.dumps(result)
			).save()
		# Если было выделение денег
		elif json.loads(deleted_action.action)['action'] == 'Increase':
			# парсинг результата действия
			for key in json.loads(deleted_action.action)["changes"].keys():
				# Запись информации о валюте/сумме которую изменяем
				result["changes"] = {
					key: -(float(json.loads(deleted_action.action)['changes'][key])),
				}
				money_balance[key] = float(money_balance[key]) - float(json.loads(deleted_action.action)['changes'][key])
			result["action"] = 'Encashment'
			result["comment"] = "Удаление операции №{0} от {1}".format(
					deleted_action.id,
					deleted_action.operation_time
			)
			# Получение денежного баланса
			money_balance = change_money_balance(result, cashbox_id)
			# Создание новой операции
			ExchangeActions(
					operation_date = datetime.date.today(),
					operation_time = datetime.datetime.now().strftime("%H:%M:%S"),
					person_data = get_object_or_404(OrdinaryCashier, id = cashbox_id),
					person_surname = request.session['0'],
					money_balance = json.dumps(money_balance),
					action = json.dumps(result)
			).save()
		# Если была обменная операция
		elif json.loads(deleted_action.action)['action'] == 'Exchange':
			pass


# Получение информации о балансе за прошлый день
def get_rest_money(rest_money_data, id):
	date = datetime.date.today()
	# Если данных за сегодня нет - получаем данные за вчерашний день, о сумме валюте
	while not rest_money_data:
		date = date.replace(day = date.day - 1)
		try:
			rest_money_data = ExchangeActions.objects.filter(person_data__id = id,
															operation_date = date
															).order_by('-id')[0]
		except:
			pass
	# Получение информации о балансе за прошлый день
	rest_money_data = json.loads(str(rest_money_data.money_balance))
	rest_money_data['date'] = date
	return rest_money_data


# Изменение баланса денег в зависимости от действий юзера
def change_money_balance(exchange_action, cashbox_id):
	# Получение последнего актуального баланса денег в кассе
	money_balance = json.loads(ExchangeActions.objects.filter(
														person_data__id = cashbox_id
														).order_by('-id')[0].money_balance
								)
	for key in exchange_action["changes"].keys():
		if exchange_action["action"] == 'Increase':
			# Вносим изменения в сумму определённой валюты
			money_balance[key] = float(money_balance[key]) + float(exchange_action["changes"][key])
		elif exchange_action["action"] == 'Encashment':
			# Вносим изменения в сумму определённой валюты
			money_balance[key] = (float(money_balance[key]) + float(exchange_action["changes"][key]))
		elif exchange_action["action"] == 'Exchange':
			# TODO Доработать обработку обменных операций
			pass
		else:
			print("*** НЕИЗВЕСТНАЯ ОПЕРАЦИЯ ***")

	return money_balance
