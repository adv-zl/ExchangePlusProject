import datetime
import json
import re

from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from .models import AdministratorScraps, ExchangeActions, ExchangeRates, Group,\
	IncreaseOperations, OrdinaryCashier, User


# TODO Заполнить документации к функциям
# TODO Закончить разделение прав юзеров на 3 группы

# основная странциа с формами и функционалом
def index(request):
	if request.user.is_anonymous():
		return HttpResponseRedirect('/login/')
	content = {}
	# Список всех касс
	content.update({'users': OrdinaryCashier.objects.all()})
	# Таблица курсов валют
	exchange_rate = ''
	# ФИО юзера которое он ввёл при входе
	person = ''
	# Проверка и получение прав доступа
	content.update(check_user_group(request))
	content.update(get_admin_messages())
	if 'OrdinaryCashier' in content['role']:
		person = OrdinaryCashier.objects.filter(user__username = request.user.username)
		person = person[0]
		# Получение последнего курса валют для данной кассы
		exchange_rate = json.loads(ExchangeRates.objects.filter(
										cashbox = person).order_by('-id')[0].exchange_rate)

	content.update({
		'doc': 'index.html',

		'user_inform': person,
		'exchange_rate_data': exchange_rate,
		'surname': request.session['0'],
	})
	return render(request, 'base.html', content)


# Главная страница с кратким описание проекта
def home(request):
	content = {
		'doc': 'home.html',
		'role': ''
	}
	if not request.user.is_anonymous():
		content['surname'] = 'Аноним'
		if request.session['0']:
			content['surname'] = request.session['0']
			# Проверка и получение прав доступа
			content.update(check_user_group(request))
			# ПОлучение списка касс
			content.update({'users': OrdinaryCashier.objects.all()})
			# ПОлучение всех сообщений для юадминистрации
			content.update(get_admin_messages())

	return render(request, 'base.html', content)


# Главная страница с кратким описание проекта
def wiki(request):
	content = {
		'doc': 'wiki.html',
		'role': ''
	}
	if not request.user.is_anonymous():
		content['surname'] = 'Аноним'
		if request.session['0']:
			content['surname'] = request.session['0']
			# Проверка и получение прав доступа
			content.update(check_user_group(request))
			# ПОлучение списка касс
			content['users'] = OrdinaryCashier.objects.all()
			# ПОлучение всех сообщений для юадминистрации
			content.update(get_admin_messages())

	return render(request, 'base.html', content)


# Форма входа юзера
def login(request):
	content = {
		'doc': 'login.html',
		'role': ''
	}
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
			content['error'] = 'Неверный логин или пароль!'
			return render(request, 'base.html', content)
	return render(request, 'base.html', content)


def logout(request):
	auth.logout(request)
	request.session = ''
	content = {
		'doc': 'logout.html',
		'role': ''
	}
	return render(request, 'base.html', content)


# Личный кабинет юзера
def private(request):
	content ={}
	# Проверка и получение прав доступа
	content.update(check_user_group(request))
	# ПОлучение списка касс
	content.update({'users': OrdinaryCashier.objects.all()})
	# ПОлучение всех сообщений для юадминистрации
	content.update(get_admin_messages())
	if 'OrdinaryCashier' in content['role']:
		return HttpResponseRedirect('/index/')
	elif request.user.is_anonymous():
		return HttpResponseRedirect('/login/')
	# Получение списка записок/трат
	scraps_list = AdministratorScraps.objects.all().order_by('-id')
	if not scraps_list:
		scraps_list = None
	content.update({'scraps_list': scraps_list})

	# Обработка форм
	if request.POST:
		# добавление записи
		if 'wasting_money_btn' in request.POST:
			AdministratorScraps(
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
			AdministratorScraps.objects.get(id = request.POST['delete_waste']).delete()
			return HttpResponseRedirect('/private/')

	content.update({
		'doc': 'private.html',

		'surname': request.session['0'],
	})
	return render(request, 'base.html', content)


# Страница создания новой кассы
def create(request):
	if request.user.is_anonymous():
		return HttpResponseRedirect('/login/')
	content ={}
	# Проверка и получение прав доступа
	content.update(check_user_group(request))
	# ПОлучение списка касс
	content.update({'users': OrdinaryCashier.objects.all()})
	# ПОлучение всех сообщений для юадминистрации
	content.update(get_admin_messages())
	if 'OrdinaryCashier' in content['role']:
		return HttpResponseRedirect('/index/')
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
			# Добавляем пользователя в выбранную группу сразу же
			group = Group.objects.get(name = request.POST['cashbox_type'])
			user.groups.add(group)
			user.save()
			# Если пользователь наблюдатель - то касса ему не нужна.
			if 'Supervisor' == request.POST['cashbox_type']:
				return HttpResponseRedirect('/index/')
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

	content.update({
		'doc': 'create_new_cashbox.html',

		'error': error,
		'surname': request.session['0'],
	})
	return render(request, 'base.html', content)


# Страница для просмотра касс
def view_cashbox(request, id):
	if request.user.is_anonymous():
		return HttpResponseRedirect('/login/')
	content ={}
	# Проверка и получение прав доступа
	content.update(check_user_group(request))
	# ПОлучение списка касс
	content.update({'users': OrdinaryCashier.objects.all()})
	# ПОлучение всех сообщений для юадминистрации
	content.update(get_admin_messages())

	# Список событий
	actions = []
	date = datetime.datetime.today()
	# Контент страницы
	content.update({
		'doc': 'view-cashbox.html',

		'id': id,
		'surname': request.session['0'],
	})
	# Получение данных определённой кассы
	certain_cashbox = get_object_or_404(OrdinaryCashier, id = id)
	content['user_inform'] = certain_cashbox
	# Вычисление прибыли кассы
	content['profit_balance'], content['profit_currencies_balance'] = profit_calculation(date, id)
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
				'operation_profit': action.operation_profit,
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
			AdministratorScraps(
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
	admin_messages = len(AdministratorScraps.objects.all())
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
		'admin_messages': admin_messages,
	}
	# ПОлучение списка всех касс
	content['users'] = OrdinaryCashier.objects.all()
	return render(request, 'base.html', content)


# Просмотр информации о кассах по дате
def cashbox_info_by_date(request):
	if request.user.is_anonymous():
		return HttpResponseRedirect('/login/')
	content ={}
	# Проверка и получение прав доступа
	content.update(check_user_group(request))
	# ПОлучение списка касс
	content.update({'users': OrdinaryCashier.objects.all()})
	# ПОлучение всех сообщений для юадминистрации
	content.update(get_admin_messages())
	if 'OrdinaryCashier' in content['role']:
		return HttpResponseRedirect('/index/')
	# Создание пустого списка курсов валют
	exchange_rate_data = ''
	content.update({
		'doc': 'cashbox_info_by_date.html',

		'surname': request.session['0'],
		'data': False,
		'exchange_rate_data': exchange_rate_data,
	})

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
															operation_date = date)
			# Если по зпдпнной юзером дате нет никакой итнформации
			if not transaction_table_data:
				content['doc'] = 'mistakes/wrong_date.html'
				content['data'] = True

				return render(request, 'base.html', content)

			content['rest_money_data'] = get_rest_money(certain_cashbox.id, date)
			try:
				exchange_rate_info = (ExchangeRates.objects.filter(
															cashbox_id = certain_cashbox.id,
															change_date = date
															).order_by('-id'))[0]
			except:
				content['doc'] = 'mistakes/wrong_date.html'
				content['data'] = True

			# Вычисление прибыли кассы
			content['profit_balance'], content['profit_currencies_balance'] = \
				profit_calculation(datetime.datetime.strptime(request.POST['date'],'%Y-%m-%d'),
									certain_cashbox.id)

		# если дату не ввёл
		else:
			# Получение данных транзакций и сумм валют определённой кассы
			transaction_table_data = ExchangeActions.objects.filter(
												person_data = certain_cashbox,
												operation_date = datetime.datetime.today())
			# Если по зпдпнной юзером дате нет никакой итнформации
			if not transaction_table_data:
				content['doc'] = 'mistakes/wrong_date.html'
				content['data'] = True

				return render(request, 'base.html', content)

			content['rest_money_data'] = get_rest_money(certain_cashbox.id,
														datetime.datetime.today())

			exchange_rate_info = ExchangeRates.objects.filter(
										cashbox_id = certain_cashbox.id).order_by('-id')[0]
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

	return render(request, 'base.html', content)


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
		# Считываем данные из форм инкассации/начисления которые передал нам юзер
		support_values, increase_rates = get_supp_encash_values(request)
		# Производим изменение баланса денег
		money_balance = change_money_balance('Increase',
											support_values,
											cashbox_id)
		cashier = get_object_or_404(OrdinaryCashier, id = cashbox_id)
		ExchangeActions.objects.create(
				operation_date = datetime.date.today(),
				operation_time = datetime.datetime.now().strftime("%H:%M:%S"),
				person_data = cashier,
				person_surname = request.session['0'],
				money_balance = json.dumps(money_balance),
				action_type = 'Increase',
				currency_changes = json.dumps(support_values),
				comment = re.sub(r'\s+', ' ', request.POST['comment']),
		).save()
		# ПОлучаем ID последней созданной нами операции
		increase_operation_id = get_object_or_404(ExchangeActions,
											currency_changes = json.dumps(support_values),
											person_data = cashier
											).id
		# Создаём отдельную запись в для мониторинга курса и подсчёта прибыли
		add_increase_values(increase_rates, cashbox_id, request, increase_operation_id)
	# Отправляем инкассацию
	elif 'encashment_btn' in request.POST:
		# Считываем данные из форм инкассации/начисления которые передал нам юзер
		encashment_values = get_supp_encash_values(request)
		# Производим изменение баланса денег
		money_balance = change_money_balance('Encashment',
											encashment_values,
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
				currency_changes = json.dumps(encashment_values),
				comment = re.sub(r'\s+', ' ', request.POST['comment'])
		).save()
		# Удаляем деньги из таблицы при инкассации средств
		delete_increase_values(encashment_values, cashbox_id, request)
	# Новая операция
	elif 'check' in request.POST:
		result["action"] = 'Exchange'
		operation_type = request.POST['operation']
		# TODO Привести к единообразию "currency_changes" и зачисление валюты в "IncreaseOperations"
		# Операция покупки валюты за гривны
		if operation_type == 's':
			currency_changes = json.dumps({
				'uah': -float(request.POST['summ_2']),
				request.POST['currency_1']: float(request.POST['summ_1'])
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
			save_buy_operation_data(request, json.loads(currency_changes),cashbox_id)

		# Операция продажи валюты населению
		elif operation_type == 'b':
			currency_changes = json.dumps({
				request.POST['currency_1']: -float(request.POST['summ_1']),
				'uah': float(request.POST['summ_2'])
			})
			operation_profit = get_operation_profit(json.loads(currency_changes),
													cashbox_id,
													request)
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
		currency_changes = {}
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
			for key in json.loads(deleted_action.currency_changes).keys():
				if json.loads(deleted_action.currency_changes)[key] != 0:
					# Запись информации о валюте/сумме которую изменяем
					currency_changes[key] = - (float(json.loads(deleted_action.currency_changes)[key]))

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
					action_type = 'Increase',
					currency_changes = json.dumps(currency_changes),
					comment = "Удаление операции №{0} от {1}".format(
															deleted_action.id,
															deleted_action.operation_time
															),
					possibility_of_operation = False
			).save()
			# Запрет использования операций начисления оперделённых средств/курсов
			IncreaseOperations.objects.filter(increase_operation_id = deleted_action.id)\
												.update(usability = True)
			# Модификация старой операции что бы её нельзя было больше удалять
			deleted_action.possibility_of_operation = False
			deleted_action.save()
		# Если было выделение денег
		elif deleted_action.action_type == 'Increase':
			# парсинг результата действия
			for key in json.loads(deleted_action.currency_changes).keys():
				if json.loads(deleted_action.currency_changes)[key] != 0:
					# Запись информации о валюте/сумме которую изменяем
					currency_changes[key] = - (float(json.loads(deleted_action.currency_changes)[key]))

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
																),
						possibility_of_operation = False
			).save()
			# Запрет использования операций начисления оперделённых средств/курсов
			IncreaseOperations.objects.filter(increase_operation_id =
												int(request.POST['delete_operation']))\
												.update(usability = False)
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
					possibility_of_operation = False,
					operation_profit = -float(deleted_action.operation_profit),
			).save()
			increase_operation = IncreaseOperations.objects.filter(
							increase_operation_id = int(request.POST['delete_operation']))
			if increase_operation[0].usability is False:
				increase_operation.update(usability = True)
			else:
				increase_operation.delete()
			# Модификация старой операции что бы её нельзя было больше удалять
			deleted_action.possibility_of_operation = False
			deleted_action.save()
	# Обработка формы выделения денег кассе
	elif 'cashbox_waste' in request.POST:
		person = get_object_or_404(OrdinaryCashier, user__username = request.user.username)
		# Производим изменение баланса денег
		money_balance = change_money_balance('Encashment',
											{
												request.POST['currency']:
												-float(request.POST['cashbox_waste_summ'])
											},
											person.id)
		if not money_balance:
			return False
		encashment_values = json.dumps({
										request.POST['currency']:
										-float(request.POST['cashbox_waste_summ'])
									})
		cashier = get_object_or_404(OrdinaryCashier, id = cashbox_id)
		cashier_admin = get_object_or_404(OrdinaryCashier, id = person.id)
		ExchangeActions.objects.create(
				operation_date = datetime.date.today(),
				operation_time = datetime.datetime.now().strftime("%H:%M:%S"),
				person_data = cashier_admin,
				person_surname = request.session['0'],
				money_balance = json.dumps(money_balance),
				action_type = 'Encashment',
				currency_changes = encashment_values,
				comment = ("Выделение денег кассе - {0}; Коментарий: ".format(cashier)
										+ re.sub(r'\s+', ' ', request.POST['comment']))
		).save()
		if request.POST['currency'] != 'uah':
			# Удаляем деньги из таблицы при инкассации средств
			delete_increase_values(json.loads(encashment_values), cashbox_id, request)
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


# Вносим изменения в таблицу валют после подкреплений
def add_increase_values(increase_rates_values, cashbox_id, request, increase_operation_id):
	# ПОлучаем данные юзера
	cashier = get_object_or_404(OrdinaryCashier, id = cashbox_id)
	surname = request.session['0']
	for currency in increase_rates_values.keys():
		if currency != 'uah' and increase_rates_values[currency]['summ'] != 0:
			IncreaseOperations.objects.create(
					operation_date = datetime.date.today(),
					operation_time = datetime.datetime.now().strftime("%H:%M:%S"),
					person_data = cashier,
					person_surname = surname,
					increase_exchange_rate = increase_rates_values[currency]['rate'],
					increase_currency = currency,
					increase_summ = increase_rates_values[currency]['summ'],
					increase_operation_id = increase_operation_id,
			).save()
	pass


# Удаляем деньги из таблицы при инкассации средств IncreaseOperations
def delete_increase_values(encashment_values, cashbox_id, request):
	"""

	:param encashment_values:
	:param cashbox_id:
	:return:
	"""
	# ПОлучаем ID полседеней операции для того что бы привязать её к инкассации
	operation_id = ExchangeActions.objects.filter(
						person_data = get_object_or_404(OrdinaryCashier, id = cashbox_id),
						currency_changes = json.dumps(encashment_values),
				).order_by('-id')[0].id
	# ПОлучаем данные юзера
	cashier = get_object_or_404(OrdinaryCashier, id = cashbox_id)
	used_encashments = {}
	for key in encashment_values.keys():
		if key != 'uah' and encashment_values[key] != 0:
			increase_operations = IncreaseOperations.objects.filter(
														person_data = cashier,
														increase_currency = key,
														usability = True)\
														.order_by('-increase_exchange_rate')
			# Циклом обходим зачисленные средства(начиная с наибольшего курса)
			# и отнимаем от них нужную нам сумму
			for i in range(0, len(increase_operations)):
				# Если сумма которую хотим обменять меньше того что есть в кассе с
				# одним курсом - просто меняем и удаляем часть суммы
				if (increase_operations[i].increase_summ + encashment_values[key]) > 0:
					# Удаляем потраченные средства
					modified_operation = get_object_or_404(IncreaseOperations,
															id = increase_operations[i].id)
					# СОхраняем сумму за которую была произведена операиця и её курс
					if key in used_encashments:
						used_encashments[key].append({
									'value': abs(encashment_values[key]),
									'rate': increase_operations[i].increase_exchange_rate
									})
					else:
						used_encashments[key] = [{
										'value': abs(encashment_values[key]),
										'rate': increase_operations[i].increase_exchange_rate
										}]

					modified_operation.increase_summ = increase_operations[i].increase_summ \
														+ encashment_values[key]
					modified_operation.save()
					break
				# Если то что мы хотим поменять больше одного зачисления в кассу -
				# отнимаем всё что есть в зачислении и с остаток от обменной суммы
				# переходим дальше
				elif (increase_operations[i].increase_summ + encashment_values[key]) < 0:
					# Обновляем данные по кол-ву денег для обмена
					encashment_values[key] = increase_operations[i].increase_summ \
																+ encashment_values[key]
					# СОхраняем сумму за которую была произведена операиця и её курс
					if key in used_encashments:
						used_encashments[key].append({
							'value': abs(increase_operations[i].increase_summ),
							'rate': increase_operations[i].increase_exchange_rate
						})
					else:
						used_encashments[key] = [{
							'value': abs(increase_operations[i].increase_summ),
							'rate': increase_operations[i].increase_exchange_rate
						}]
					# Удаляем потраченные средства
					modified_operation = get_object_or_404(IncreaseOperations,
															id = increase_operations[i].id)
					modified_operation.delete()
				# Если сумма для обмена равна сумме что осталась в кассе
				else:
					# СОхраняем сумму за которую была произведена операиця и её курс
					if key in used_encashments:
						used_encashments[key].append({
							'value': abs(encashment_values[key]),
							'rate': increase_operations[i].increase_exchange_rate
						})
					else:
						used_encashments[key] = [{
							'value': abs(encashment_values[key]),
							'rate': increase_operations[i].increase_exchange_rate
						}]
					# Удаляем потраченные средства
					IncreaseOperations.objects.filter(id = increase_operations[i].id)\
																.update(usability = False)
					break

			for element in used_encashments[key]:
				IncreaseOperations(
							person_data = get_object_or_404(OrdinaryCashier, id = cashbox_id),
							person_surname = request.session['0'],
							increase_exchange_rate = element['rate'],
							increase_currency = key,
							increase_operation_id = operation_id,
							increase_summ = element['value'],
							operation_date = datetime.date.today(),
							operation_time = datetime.datetime.now().strftime("%H:%M:%S"),
							usability = False,
					).save()


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

	return round(profit_balance, 2), profit_currencies_balance


# Получение чистой прибыли отдельной операции
def get_operation_profit(currency_changes, cashbox_id, request):
	used_exchanges = {}
	operation_profit = 0
	# ПОлучаем ID полседеней операции для того что бы привязать её к инкассации
	operation_id = ExchangeActions.objects.filter(
						person_data = get_object_or_404(OrdinaryCashier, id = cashbox_id),
				).order_by('-id')[0].id + 1
	exchange_rate = json.loads((ExchangeRates.objects.filter(cashbox__id = cashbox_id)
														.order_by('-id'))[0].exchange_rate)
	# ПОлучаем данные юзера
	cashier = get_object_or_404(OrdinaryCashier, id = cashbox_id)
	for key in currency_changes.keys():
		if key != 'uah':
			increase_operations = IncreaseOperations.objects.filter(
														person_data = cashier,
														increase_currency = key,
														usability = True)\
														.order_by('-increase_exchange_rate')
			# Циклом обходим зачисленные средства(начиная с наименьшего курса)
			# и отнимаем от них нужную нам сумму
			for i in range(0, len(increase_operations)):
				# Если сумма которую хотим обменять меньше того что есть в кассе с
				# одним курсом - просто меняем и удаляем часть суммы
				if (increase_operations[i].increase_summ + currency_changes[key]) > 0:
					operation_profit += round(-exchange_rate[key+'_sell']
											* currency_changes[key]\
											+ currency_changes[key]\
											* increase_operations[i].increase_exchange_rate,
										2)
					# Удаляем потраченные средства
					modified_operation = get_object_or_404(IncreaseOperations,
															id = increase_operations[i].id)
					# СОхраняем сумму за которую была произведена операиця и её курс
					if key in used_exchanges:
						used_exchanges[key].append({
							'value': abs(currency_changes[key]),
							'rate': increase_operations[i].increase_exchange_rate
						})
					else:
						used_exchanges[key] = [{
							'value': abs(currency_changes[key]),
							'rate': increase_operations[i].increase_exchange_rate
						}]

					modified_operation.increase_summ = increase_operations[i].increase_summ \
														+ currency_changes[key]
					modified_operation.save()
					break
				# Если то что мы хотим поменять больше одного зачисления в кассу -
				# отнимаем всё что есть в зачислении и с остаток от обменной суммы
				# переходим дальше
				elif (increase_operations[i].increase_summ + currency_changes[key]) < 0:
					operation_profit += round(-exchange_rate[key + '_sell']
											* currency_changes[key]\
											+ currency_changes[key]\
											* increase_operations[i].increase_exchange_rate,
											2)
					# Обновляем данные по кол-ву денег для обмена
					currency_changes[key] = increase_operations[i].increase_summ \
																	+ currency_changes[key]
					# СОхраняем сумму за которую была произведена операиця и её курс
					if key in used_exchanges:
						used_exchanges[key].append({
							'value': abs(increase_operations[i].increase_summ),
							'rate': increase_operations[i].increase_exchange_rate
						})
					else:
						used_exchanges[key] = [{
							'value': abs(increase_operations[i].increase_summ),
							'rate': increase_operations[i].increase_exchange_rate
						}]
					# Удаляем потраченные средства
					modified_operation = get_object_or_404(IncreaseOperations,
															id = increase_operations[i].id)
					modified_operation.delete()
				# Если сумма для обмена равна сумме что осталась в кассе
				else:
					operation_profit += round(-exchange_rate[key + '_sell']
											* currency_changes[key]\
											+ currency_changes[key]\
											* increase_operations[i].increase_exchange_rate,
											2)
					# СОхраняем сумму за которую была произведена операиця и её курс
					if key in used_exchanges:
						used_exchanges[key].append({
							'value': abs(currency_changes[key]),
							'rate': increase_operations[i].increase_exchange_rate
						})
					else:
						used_exchanges[key] = [{
							'value': abs(currency_changes[key]),
							'rate': increase_operations[i].increase_exchange_rate
						}]
					# Удаляем потраченные средства
					IncreaseOperations.objects.filter(id = increase_operations[i].id)\
																.update(usability = False)
					break

			for element in used_exchanges[key]:
				IncreaseOperations(
						person_data = get_object_or_404(OrdinaryCashier, id = cashbox_id),
						person_surname = request.session['0'],
						increase_exchange_rate = element['rate'],
						increase_currency = key,
						increase_operation_id = operation_id,
						increase_summ = element['value'],
						operation_date = datetime.date.today(),
						operation_time = datetime.datetime.now().strftime("%H:%M:%S"),
						usability = False,
				).save()

	return round(operation_profit, 2)


# СОхраняем в прибыток валюту полученную при покупке и курс
def save_buy_operation_data(request, currency_changes, cashbox_id):
	"""
	Сохраняет в IncreaseOperations данные после обменной операции юзера по покупке
	валюты у населения
	:param request: реквест от юзера
	:param currency_changes:
	:param cashbox_id: номер кассы на которой совершон обмен
	:return: нисчего не возвращает, просто производит операцию
	"""
	cashier = get_object_or_404(OrdinaryCashier, id = cashbox_id)
	exchange_rate = json.loads((ExchangeRates.objects.filter(cashbox__id = cashbox_id)
													.order_by('-id'))[0].exchange_rate)
	operation = ExchangeActions.objects.filter(
										person_data = cashier,
										currency_changes = json.dumps(currency_changes))
	operation_id = operation.order_by('-id')[0].id
	for key in currency_changes.keys():
		if key != 'uah':
			IncreaseOperations(
					person_data = cashier,
					person_surname = request.session['0'],
					increase_exchange_rate = exchange_rate[key+'_buy'],
					increase_currency = key,
					increase_operation_id = operation_id,
					increase_summ = currency_changes[key],
					operation_date = datetime.date.today(),
					operation_time = datetime.datetime.now().strftime("%H:%M:%S"),
			).save()


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


# Получаем валюту и курс после подкрепления/инкассации
def get_supp_encash_values(request):
	try:
		# Валюта и сумма
		support_values = {
			"uah": float(request.POST['uah_support']),
			"usd": float(request.POST['usd_support']),
			"eur": float(request.POST['eur_support']),
			"rub": float(request.POST['rub_support']),
			"cad": float(request.POST['cad_support']),
			"chf": float(request.POST['chf_support']),
			"gbp": float(request.POST['gbp_support']),
			"pln": float(request.POST['pln_support']),
		}
		# Валюта{сумма, курс}
		increase_rates = {
			"uah": {'summ': float(request.POST['uah_support']),
					'rate': float(request.POST['uah_increase_exchange_rate'])},
			"usd": {'summ': float(request.POST['usd_support']),
					'rate': float(request.POST['usd_increase_exchange_rate'])},
			"eur": {'summ': float(request.POST['eur_support']),
					'rate': float(request.POST['eur_increase_exchange_rate'])},
			"rub": {'summ': float(request.POST['rub_support']),
					'rate': float(request.POST['rub_increase_exchange_rate'])},
			"cad": {'summ': float(request.POST['cad_support']),
					'rate': float(request.POST['cad_increase_exchange_rate'])},
			"chf": {'summ': float(request.POST['chf_support']),
					'rate': float(request.POST['chf_increase_exchange_rate'])},
			"gbp": {'summ': float(request.POST['gbp_support']),
					'rate': float(request.POST['gbp_increase_exchange_rate'])},
			"pln": {'summ': float(request.POST['pln_support']),
					'rate': float(request.POST['pln_increase_exchange_rate'])},
		}
		return support_values, increase_rates
	except:
		encashment_values = {
			"uah": -float(request.POST['uah_encashment']),
			"usd": -float(request.POST['usd_encashment']),
			"eur": -float(request.POST['eur_encashment']),
			"rub": -float(request.POST['rub_encashment']),
			"cad": -float(request.POST['cad_encashment']),
			"chf": -float(request.POST['chf_encashment']),
			"gbp": -float(request.POST['gbp_encashment']),
			"pln": -float(request.POST['pln_encashment']),
		}
		return encashment_values


# Проверяем права доступа пользователя
def check_user_group(request):
	'''
	Функция для опеределения прав доступа пользователя. Бывает три типа прав:
	1. Администратор - создаёт кассы/операции, удаляет операции, редактирует кассы.
	2. Обычный кассир - создаёт операции.
	3. Наблюдатель - может лишь просматривать информацию но без права редактирования
	:param request: получаем реквест с информацией о юзере
	:return: возвращаем словарь с типом прав юзера
	'''
	if request.user.groups.filter(name = 'ChiefCashier').exists():
		return {'role': 'ChiefCashier'}
	elif request.user.groups.filter(name = 'OrdinaryCashier').exists():
		return {'role': 'OrdinaryCashier'}
	elif request.user.groups.filter(name = 'Supervisor').exists():
		return {'role': 'Supervisor'}
	else:
		return {'role': ''}


# ПОлучение всех сообещений для администрации
def get_admin_messages():
	# ПОлучение списка всех записок
	admin_messages = len(AdministratorScraps.objects.all())
	return {'admin_messages': admin_messages}