from django.shortcuts import render, get_object_or_404
from django.contrib import auth
from django.http import HttpResponseRedirect
from .models import AdministratorCashCosts, ExchangeRates, OrdinaryCashier, \
	ExchangeActions, User
import json
import datetime
import re
# TODO Заполнить документации к функциям


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
		# Получение последнего курса валют для данной кассы
		exchange_rate = json.loads(ExchangeRates.objects.filter(
										cashbox = person).order_by('-id')[0].exchange_rate)

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
			content['users'] = OrdinaryCashier.objects.all()

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
			content['users'] = OrdinaryCashier.objects.all()

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
	waste_list = AdministratorCashCosts.objects.all().order_by('-id')
	if not waste_list:
		waste_list = None

	# Обработка форм
	if request.POST:
		# добавление записи
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
		# удаление записи
		elif 'delete_waste' in request.POST:
			AdministratorCashCosts.objects.get(id = request.POST['delete_waste']).delete()
			return HttpResponseRedirect('/private/')

	content = {
		'doc': 'profile.html',

		'role': True,
		'waste_list': waste_list,
		'surname': request.session['0'],
		'admin_messages': admin_messages
	}
	# ПОлучение списка всех касс
	content['users'] = OrdinaryCashier.objects.all()
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
	error = False

	# Обработка форм
	if request.POST:
		user, created = User.objects.get_or_create(username = request.POST['username'])
		if not created:
			error = True
		else:
			date = datetime.date.today()
			# Создаём нового юзера
			user.set_password(request.POST['password'])
			user.save()
			# Считываем описание кассы
			cashier_description_full = request.POST['description_full']
			cashier_description_short = request.POST['description_short']
			# Сохраняем данные
			OrdinaryCashier.objects.create(
					user = user,
					cashier_description_full = cashier_description_full,
					cashier_description_short = cashier_description_short,
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
					action_type = 'Новая касса',
					currency_changes = json.dumps({
												"uah": 0,
												"usd": 0,
												"eur": 0,
												"rub": 0,
												"cad": 0,
												"chf": 0,
												"gbp": 0,
												"pln": 0
												}),
					comment = "Начальный баланс",
			).save()
			# Создаём курс валют для данной кассы
			ExchangeRates.objects.create(
					exchange_rate = get_exchange_rate(request),
					cashbox = get_object_or_404(OrdinaryCashier, user = user),
					change_date = datetime.date.today(),
					change_time = datetime.datetime.now().strftime("%H:%M:%S"),
			)

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
	date = datetime.datetime.today()
	# Контент страницы
	content = {
		'doc': 'view-cashbox.html',

		'id': id,
		'role': role,
		'admin_messages': admin_messages,
		'surname': request.session['0'],
	}
	# ПОлучение списка всех касс
	content['users'] = OrdinaryCashier.objects.all()
	# Получение данных определённой кассы
	certain_cashbox = get_object_or_404(OrdinaryCashier, id = id)
	content['user_inform'] = certain_cashbox
	# Вычисление прибыли кассы
	content['profit_balance'], content['profit_currencies_balance'] = profit_calculation(
			date, id)
	# Получение данных транзакций и сумм валют определённой кассы
	transaction_table_data = ExchangeActions.objects.filter(person_data__id = id,
															operation_date = date)

	content['rest_money_data'] = get_rest_money(id, date)

	if transaction_table_data:
		for action in transaction_table_data:
			actions.append({
				"action": action,
				# Получение данных о балансе
				"money_balance_data": json.loads(str(action.money_balance)),
				# Получение данных о операциях
				"action_type": action.action_type,
				"currency_changes": json.loads(action.currency_changes),
				"action_comment": action.comment,
			})
		content['actions'] = actions
	# Курсы валют
	content['exchange_rate_data'] = json.loads((ExchangeRates.objects.filter(cashbox = certain_cashbox)
												.order_by('-id'))[0].exchange_rate)

	# Обработка форм
	if request.POST:
		# Вносим изменения в курсы валют
		if 'exchange_rate_save' in request.POST:
			ExchangeRates.objects.create(
					exchange_rate = get_exchange_rate(request),
					cashbox = certain_cashbox,
					change_date = datetime.date.today(),
					change_time = datetime.datetime.now().strftime("%H:%M:%S"),
			).save()
			return HttpResponseRedirect('/view-cashbox/{0}'.format(id))
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
			if count_result_of_action(request, id):
				return HttpResponseRedirect('/view-cashbox/{0}'.format(id))
			else:
				content['error'] = True
				return render(request, 'base.html', content)

	return render(request, 'base.html', content)


# Страница для изменения кассы
def edit_cashbox(request, id):
	if request.user.is_anonymous():
		return HttpResponseRedirect('/login/')
	# Проверка прав доступа
	if not request.user.has_perm('ExchangeHelper.delete_exchangeactions'):
		return HttpResponseRedirect('/index/')
	# ПОлучение списка всех записок
	admin_messages = len(AdministratorCashCosts.objects.all())
	# Получение определённой кассы
	certain_cashbox = get_object_or_404(OrdinaryCashier, id = id)
	exchange_rate = json.loads(ExchangeRates.objects.filter(cashbox = certain_cashbox)
														.order_by('-id')[0].exchange_rate)

	if request.POST:
		# Сохраняем данные
		certain_cashbox.user.username = request.POST['username']
		certain_cashbox.cashier_description_full = request.POST['description_full']
		certain_cashbox.cashier_description_short = request.POST['description_short']
		certain_cashbox.save()
		# Создаём курс валют для данной кассы
		ExchangeRates.objects.create(
				exchange_rate = get_exchange_rate(request),
				cashbox = certain_cashbox,
				change_date = datetime.date.today(),
				change_time = datetime.datetime.now().strftime("%H:%M:%S"),
		).save()

		return HttpResponseRedirect('/index/')

	content = {
		'doc': 'edit_cashbox.html',

		'cashbox_data': certain_cashbox,
		'exchange_rate_data': exchange_rate,
		'surname': request.session['0'],
		'role': True,
		'admin_messages': admin_messages,
	}
	# ПОлучение списка всех касс
	content['users'] = OrdinaryCashier.objects.all()
	return render(request, 'base.html', content)


# Просмотр информации о кассах по дате
def cashbox_info_by_date(request):
	if request.user.is_anonymous():
		return HttpResponseRedirect('/login/')
	# Проверка прав доступа
	if not request.user.has_perm('ExchangeHelper.delete_exchangeactions'):
		return HttpResponseRedirect('/index/')
	# ПОлучение списка всех записок
	admin_messages = len(AdministratorCashCosts.objects.all())
	# Получение списка всех касс
	cashbox_list = OrdinaryCashier.objects.all()
	# Создание пустого списка курсов валют
	exchange_rate_data = ''
	content = {
				'doc': 'cashbox_info_by_date.html',

				'cashbox_list': cashbox_list,
				'surname': request.session['0'],
				'role': True,
				'data': False,
				'exchange_rate_data': exchange_rate_data,
				'admin_messages': admin_messages,
			}
	# ПОлучение списка всех касс
	content['users'] = OrdinaryCashier.objects.all()

	# Получение определённой кассы

	if request.POST:
		# Если решил удалить операцию
		if 'delete_operation' in request.POST:
			return HttpResponseRedirect('/financial-statement/')
		certain_cashbox = OrdinaryCashier.objects.get(id = request.POST['selected_cashbox'])
		# Если юзер ввёл дату
		if request.POST['date']:
			date = datetime.datetime.strptime(request.POST['date'],'%Y-%m-%d')
			# Получение данных транзакций и сумм валют определённой кассы за
			# определённую дату
			transaction_table_data = ExchangeActions.objects.filter(
																	person_data = certain_cashbox,
																	operation_date = date
																	)
			# Если по зпдпнной юзером дате нет никакой итнформации
			if not transaction_table_data:
				content['doc'] = 'mistakes/wrong_date.html'
				content['data'] = True

				return render(request, 'base.html', content)

			content['rest_money_data'] = get_rest_money(certain_cashbox.id, date)

			exchange_rate_info = (ExchangeRates.objects.filter(
														cashbox_id = certain_cashbox.id,
														change_date = date
														).order_by('-id'))[0]
			# Вычисление прибыли кассы
			content['profit_balance'], content['profit_currencies_balance'] = \
				profit_calculation(datetime.datetime.strptime(request.POST['date'],'%Y-%m-%d'),
									certain_cashbox.id)

		# если дату не ввёл
		else:
			# Получение данных транзакций и сумм валют определённой кассы
			transaction_table_data = ExchangeActions.objects.filter(
													person_data = certain_cashbox,
													operation_date = datetime.datetime.today()
													)
			# Если по зпдпнной юзером дате нет никакой итнформации
			if not transaction_table_data:
				content['doc'] = 'mistakes/wrong_date.html'
				content['data'] = True

				return render(request, 'base.html', content)

			content['rest_money_data'] = get_rest_money(certain_cashbox.id,
														datetime.datetime.today())

			exchange_rate_info = ExchangeRates.objects.filter(cashbox_id = certain_cashbox.id
																).order_by('-id')[0]
			# Вычисление прибыли кассы
			content['profit_balance'], content['profit_currencies_balance'] = \
				profit_calculation(datetime.datetime.today(),
															certain_cashbox.id)
		# Записываем все действия в список
		actions = []
		for action in transaction_table_data:
			actions.append({
				"action": action,
				# Получение данных о балансе
				"money_balance_data": json.loads(str(action.money_balance)),
				# Получение данных о операциях
				"action_type": action.action_type,
				"currency_changes": json.loads(action.currency_changes),
				"action_comment": action.comment,
			})
		content['actions'] = actions

		exchange_rate_data = json.loads(exchange_rate_info.exchange_rate)
		content['exchange_rate_data'] = exchange_rate_data
		content['exchange_rate_info'] = exchange_rate_info
		content['data'] = True
		content['role'] = False

	return render(request, 'base.html', content)


# Получаем значения курсов валют со страницы
def get_exchange_rate(request):
	"""
	
	:param request: 
	:return: 
	"""
	return json.dumps({
				"usd_buy": float(request.POST['usd_buy']),
				"usd_sell": float(request.POST['usd_sell']),
				"eur_buy": float(request.POST['eur_buy']),
				"eur_sell": float(request.POST['eur_sell']),
				"rub_buy": float(request.POST['rub_buy']),
				"rub_sell": float(request.POST['rub_sell']),
				"cad_buy": float(request.POST['cad_buy']),
				"cad_sell": float(request.POST['cad_sell']),
				"chf_buy": float(request.POST['chf_buy']),
				"chf_sell": float(request.POST['chf_sell']),
				"gbp_buy": float(request.POST['gbp_buy']),
				"gbp_sell": float(request.POST['gbp_sell']),
				"pln_buy": float(request.POST['pln_buy']),
				"pln_sell": float(request.POST['pln_sell']),
			})


# Обработчик действий выдачи средств/инкассации и операций обмена
def count_result_of_action(request, cashbox_id):
	"""
	Реализация действий юзера: выделение денег, инкассация, создание новой операции, 
	удаление операции
	:param request: Принимает в качестве параметра POST запро и на основе того что 
	выбрал юзер - вычисляет результат и производит действия 
	:param cashbox_id: Номер кассы с которой был послан POST запрос
	:return: Ничего не возвращает, лишь создаёт новые операции в БД 
	или изменяет старые и сохраняет.
	"""
	result = {}
	# Выделяем денежную поддержку кассе
	if 'support_btn' in request.POST:
		# Производим изменение баланса денег
		money_balance = change_money_balance('Increase',
											{
												request.POST['currency']:
												request.POST['support_summ']
											},
											cashbox_id)
		cashier = get_object_or_404(OrdinaryCashier, id = cashbox_id)
		ExchangeActions.objects.create(
				operation_date = datetime.date.today(),
				operation_time = datetime.datetime.now().strftime("%H:%M:%S"),
				person_data = cashier,
				person_surname = request.session['0'],
				money_balance = json.dumps(money_balance),
				action_type = 'Increase',
				currency_changes = json.dumps({request.POST['currency']:
												request.POST['support_summ']}
											),
				comment = re.sub(r'\s+', ' ', request.POST['comment'])
		).save()
	# Отправляем инкассацию
	elif 'encashment_btn' in request.POST:
		# Производим изменение баланса денег
		money_balance = change_money_balance('Encashment',
											{
												request.POST['currency']:
												-float(request.POST['encashment_summ'])
											},
											cashbox_id)
		if not money_balance:
			return False
		cashier = get_object_or_404(OrdinaryCashier, id = cashbox_id)
		ExchangeActions.objects.create(
				operation_date = datetime.date.today(),
				operation_time = datetime.datetime.now().strftime("%H:%M:%S"),
				person_data = cashier,
				person_surname = request.session['0'],
				money_balance = json.dumps(money_balance),
				action_type = 'Encashment',
				currency_changes = json.dumps({
												request.POST['currency']:
												-float(request.POST['encashment_summ'])
												}),
				comment = re.sub(r'\s+', ' ', request.POST['comment'])
		).save()
	# Новая операция
	elif 'check' in request.POST:
		result["action"] = 'Exchange'
		operation_type = request.POST['operation']

		# Операция покупки валюты за гривны
		if operation_type == 's':
			currency_changes = json.dumps({
				'uah': -float(request.POST['summ_2']),
				request.POST['currency_1']: float(request.POST['summ_1'])
			})
			operation_profit = get_operation_profit(json.loads(currency_changes),
													cashbox_id)
		# Операция продажи валюты населению
		elif operation_type == 'b':
			currency_changes = json.dumps({
				request.POST['currency_1']: -float(request.POST['summ_1']),
				'uah': float(request.POST['summ_2'])
			})
			operation_profit = 0

		# Изменяем баланс денег в кассе
		money_balance = change_money_balance('Exchange',
											json.loads(currency_changes),
											cashbox_id)
		cashier = get_object_or_404(OrdinaryCashier, id = cashbox_id)
		# Создаём новую операцию
		ExchangeActions.objects.create(
				operation_date = datetime.date.today(),
				operation_time = datetime.datetime.now().strftime("%H:%M:%S"),
				person_data = cashier,
				person_surname = request.session['0'],
				money_balance = json.dumps(money_balance),
				action_type = 'Exchange',
				currency_changes = currency_changes,
				comment = 'Обменная операция.',
				operation_profit = operation_profit,
		).save()
	# Удаление операций
	elif 'delete_operation' in request.POST:
		# Получение данных об операции которую хотим удалить, по id
		deleted_action = ExchangeActions.objects.get(id = int(request.POST['delete_operation']))
		# Получение актуального баланса денег в кассе по номеру кассы и дате
		money_balance = json.loads(ExchangeActions.objects.filter(
															person_data__id = cashbox_id,
															operation_date = deleted_action.operation_date
															).order_by('-id')[0].money_balance
								)

		# Если была инкассация
		if deleted_action.action_type == 'Encashment':
			# парсинг результата действия
			for key in json.loads(deleted_action.currency_changes).keys():
				# Запись информации о валюте/сумме которую изменяем
				currency_changes = {
									key: -(float(json.loads(
													deleted_action.currency_changes)[key])),
									}
				money_balance[key] = float(money_balance[key]) \
									- float(json.loads(deleted_action.currency_changes)[key])
			# Получение денежного баланса
			money_balance = change_money_balance('Increase',
												currency_changes,
												cashbox_id
												)
			# Создание новой операции
			ExchangeActions(
					operation_date = datetime.date.today(),
					operation_time = datetime.datetime.now().strftime("%H:%M:%S"),
					person_data = get_object_or_404(OrdinaryCashier, id = cashbox_id),
					person_surname = request.session['0'],
					money_balance = json.dumps(money_balance),
					action_type = 'Increase',
					currency_changes = json.dumps(currency_changes),
					comment = "Удаление операции №{0} от {1}".format(
															deleted_action.id,
															deleted_action.operation_time
															)
			).save()
			# Модификация старой операции что бы её нельзя было больше удалять
			deleted_action.possibility_of_operation = False
			deleted_action.save()
		# Если было выделение денег
		elif deleted_action.action_type == 'Increase':
			# парсинг результата действия
			for key in json.loads(deleted_action.currency_changes).keys():
				# Запись информации о валюте/сумме которую изменяем
				currency_changes = {
									key: - (float(json.loads(
													deleted_action.currency_changes)[key])),
									}
				money_balance[key] = float(money_balance[key])\
									+ float(json.loads(
													deleted_action.currency_changes)[key])
			# Получение денежного баланса
			money_balance = change_money_balance('Encashment',
												currency_changes,
												cashbox_id
												)
			# Создание новой операции
			ExchangeActions(
					operation_date = datetime.date.today(),
					operation_time = datetime.datetime.now().strftime("%H:%M:%S"),
					person_data = get_object_or_404(OrdinaryCashier, id = cashbox_id),
					person_surname = request.session['0'],
					money_balance = json.dumps(money_balance),
					action_type = 'Encashment',
					currency_changes = json.dumps(currency_changes),
					comment = "Удаление операции №{0} от {1}".format(
															deleted_action.id,
															deleted_action.operation_time
															)
			).save()
			# Модификация старой операции что бы её нельзя было больше удалять
			deleted_action.possibility_of_operation = False
			deleted_action.save()
		# Если была обменная операция
		elif deleted_action.action_type == 'Exchange':
			# Сюда будут записаны изменения валют
			currency_changes = {}
			# парсинг результата действия
			for key in json.loads(deleted_action.currency_changes).keys():
				# Запись информации о валюте/сумме которую изменяем
				currency_changes[key] = - float(json.loads(deleted_action.currency_changes)[key])
				money_balance[key] = float(money_balance[key])\
									+ float(json.loads(deleted_action.currency_changes)[key])
			# Получение денежного баланса
			money_balance = change_money_balance('Exchange',
												currency_changes,
												cashbox_id
												)
			# Создание новой операции
			ExchangeActions(
					operation_date = datetime.date.today(),
					operation_time = datetime.datetime.now().strftime("%H:%M:%S"),
					person_data = get_object_or_404(OrdinaryCashier, id = cashbox_id),
					person_surname = request.session['0'],
					money_balance = json.dumps(money_balance),
					action_type = 'Exchange',
					currency_changes = json.dumps(currency_changes),
					comment = "Удаление обменной операции №{0} от {1}".format(
															deleted_action.id,
															deleted_action.operation_time
															),
					possibility_of_operation = True
			).save()

			# Модификация старой операции что бы её нельзя было больше удалять
			deleted_action.possibility_of_operation = False
			deleted_action.save()
	# Обработка формы выделения денег кассе
	elif 'cashbox_waste' in request.POST:
		# Производим изменение баланса денег
		# TODO Выцеплять ID админа кассы а не писать единицу
		money_balance = change_money_balance('Encashment',
											{
												request.POST['currency']:
												-float(request.POST['cashbox_waste_summ'])
											},
											1)
		if not money_balance:
			return False
		cashier = get_object_or_404(OrdinaryCashier, id = cashbox_id)
		cashier_admin = get_object_or_404(OrdinaryCashier, id = 1)
		ExchangeActions.objects.create(
				operation_date = datetime.date.today(),
				operation_time = datetime.datetime.now().strftime("%H:%M:%S"),
				person_data = cashier_admin,
				person_surname = request.session['0'],
				money_balance = json.dumps(money_balance),
				action_type = 'Encashment',
				currency_changes = json.dumps({
					request.POST['currency']:
						-float(request.POST['cashbox_waste_summ'])
				}),
				comment = ("Выделение денег кассе - {0}; Коментарий: ".format(cashier)
										+ re.sub(r'\s+', ' ', request.POST['comment']))
		).save()
	return True


# Получение информации о балансе за прошлый день
def get_rest_money(id, date):
	"""
	Получаем информацию о балансе за прошлый рабочий день, максимальный срок - 2 
	месяца, иначе операция считается невыполнимой.
	:param id: Получаем ID кассы по которой делается выборка по последнему балансу 
	за прошлый день 
	:param date: Дата последней оперции сделанной не сегодня 
	:return: Возвращает словарь значений состоящий из баланса денег после последней 
	операции и дате выборки
	"""
	rest_money_data = None
	if date > datetime.datetime.today():
		date = datetime.date.today()
	# Предельная глубина поиска от заданой даты
	max_depth = date.month - 2
	# Если данных за сегодня нет - получаем данные за вчерашний день, о сумме валюте
	while date.month >= max_depth and not rest_money_data:
		date = date - datetime.timedelta(days = 1)
		try:
			rest_money_data = (ExchangeActions.objects.filter(person_data__id = id,
																operation_date = date
																).order_by('-id'))[0]
		except:
			pass
	# Получение информации о балансе за прошлый день
	rest_money_data = json.loads(str(rest_money_data.money_balance))
	rest_money_data['date'] = date.date()
	return rest_money_data


# Изменение баланса денег в зависимости от действий юзера
def change_money_balance(action_type, currency_changes, cashbox_id):
	"""
	Изменение баланса кассы в зависимости от типа операции которую провёл юзер.
	:param action_type: Передаётся тип операции, их всего 3 "Внесение 
	средств/Инкассация/Обмен валют" - "Increase/Encashment/Exchange" соответственно
	:param currency_changes: Получаем словарь в котором представлены изменения курса 
	валют, вид имеет: {%currency%: +/-%summ%}
	:param cashbox_id: Получаем ID конкретной кассы в которой произошла операция(это 
	используется для выборки денежного баланса опеределённой кассы)
	:return: Возвращает обновлённый денежный баланс кассы, так же в виде словаря:
		{
			%currency%: %summ%,
			и так для всех используемых валют
		}
	"""
	# Получение последнего актуального баланса денег в кассе
	money_balance = json.loads(ExchangeActions.objects.filter(person_data__id = cashbox_id)
								.order_by('-id')[0].money_balance
								)

	for key in currency_changes.keys():
		if action_type == 'Increase':
			# Вносим изменения в сумму определённой валюты
			money_balance[key] = round(float(money_balance[key]) +
														float(currency_changes[key]), 3)
		elif action_type == 'Encashment':
			# Если в кассе денег меньше чем мы хотим снять
			if float(money_balance[key]) < -(float(currency_changes[key])):
				return False
			else:
				# Вносим изменения в сумму определённой валюты
				money_balance[key] = round(float(money_balance[key]) +
															float(currency_changes[key]), 3)
		elif action_type == 'Exchange':
			money_balance[key] = round(float(money_balance[key])
															+ currency_changes[key], 3)

	return money_balance


# Подсчёт прибыли за сутки
# Учитывается лишь прибыль от обменных операций
def profit_calculation(date, id):
	"""
	Результат всех обменных операций за день по валютам складывается и получается сумма всего что 
	касса наторговала за день.
	:param date: Получает дату по которой делается выборка всех ОБМЕННЫХ операций и 
	происходит их подсчёт
	:param id: Получает ID кассы и так же делает выборку по нему и параметру даты
	:return: Возвращает в словаря сумму всего наторгованного в кассе по определённой дате
	"""
	# TODO ПОдсчитывать прибыль от операций сразу на момент проведения обменной
	# операции и сразу сохранять результат в БД
	profit_balance = 0
	# Профицит за день
	profit_currencies_balance = {
						"uah": 0,
						"usd": 0,
						"eur": 0,
						"rub": 0,
						"cad": 0,
						"chf": 0,
						"gbp": 0,
						"pln": 0,
					}
	# Получение списка всех обменных операций данной кассы в данный день
	exchange_data = ExchangeActions.objects.filter(person_data__id = id,
													operation_date = date,
													action_type = 'Exchange',)
	for operation in exchange_data:
		# Подсчитываем профицит общий
		profit_balance += operation.operation_profit
		for key in json.loads(operation.currency_changes).keys():
			# Вносим изменения в профицит по валютам
			profit_currencies_balance[key] = round(float(profit_currencies_balance[key])
									+ float(json.loads(operation.currency_changes)[key]), 3)

	return profit_balance, profit_currencies_balance


# Получение чистой прибыли отдельной операции
def get_operation_profit(currency_changes, cashbox_id):
	operation_profit = 0
	exchange_rate = json.loads((ExchangeRates.objects.filter(cashbox__id = cashbox_id)
								.order_by('-id'))[0].exchange_rate)
	for key in currency_changes.keys():
		if key == 'uah':
			operation_profit += currency_changes[key]
		else:
			operation_profit += round(exchange_rate[key+'_sell'] * currency_changes[key], 2)
	return operation_profit
