from django.contrib.auth.models import Group, User
from django.db import models


# Создание рядовойго кассира
class OrdinaryCashier(models.Model):# Логин кассира
	user = models.ForeignKey(User)
	# ПОлное описание кассы
	cashier_description_full = models.CharField(max_length = 600)
	# Краткое описание кассы
	cashier_description_short = models.CharField(max_length = 100)

	def __str__(self):
		return ('№ ' + str(self.id) + '. Логин: ' + str(self.user.username) +
				'. Описание: ' + str(self.cashier_description_short))


# Таблица действий юзера и учёта суммы денег
class ExchangeActions(models.Model):
	# Дата операции
	operation_date = models.DateField()
	# Время операции
	operation_time = models.TimeField()
	# Данные кассы
	person_data = models.ForeignKey(OrdinaryCashier)
	# ФИО кассира проведшего операцию
	person_surname = models.CharField(max_length = 20)
	# Список валют в кассе и их баланс
	money_balance = models.CharField(max_length = 200)
	# Тип операции  "Инкасация/Обмен/Пополнение" - "Encashment / Exchange / Increase"
	action_type = models.CharField(max_length = 20)
	# Изменение кол-ва валюты:
	# инкасация/попленение {
	# 'currency': 'summ'
	# },
	# обмен: {
	# 'currency_get': 'summ' >0,
	# 'currency_put': 'summ' <0
	# }
	currency_changes = models.CharField(max_length = 100)
	# ПРибыль от обменно операции
	operation_profit = models.FloatField(default = 0)
	# Коментарий к событию
	comment = models.CharField(max_length = 200, default = ' ')
	# Активна ли операция, если да то она поерация обмена иона не удалённая
	possibility_of_operation = models.BooleanField(default = True)

	def __str__(self):
		return ('№ '+ str(self.id) +
				'. ' +str(self.operation_date)+', '+ str(self.operation_time)+
				'. Тип операции: ' + str(self.action_type) +
				'. Изменение валют: '+str(self.currency_changes)+';')


# Записки для односторонней связи кассир->админ и для записей трат администратора
class AdministratorScraps(models.Model):
	# Данные кассы
	waste_cashbox = models.ForeignKey(OrdinaryCashier)
	# ФИО автора записки
	waste_author = models.CharField(max_length = 20)
	# Причина траты
	waste_reason = models.CharField(max_length = 300)
	# Сумма трат
	waste_summ = models.FloatField()
	# Валюта для траты
	waste_currency = models.CharField(max_length = 4)
	# Коментарий к тратам
	waste_comment = models.CharField(max_length = 600)
	# Дата операции
	waste_date = models.DateField()
	# Время операции
	waste_time = models.TimeField()

	def __str__(self):
		return ('От '+ str(self.waste_author) +
				', из: '+ str(self.waste_cashbox.cashier_description_short) +
				'. Причина: ' +str(self.waste_reason)+
				'; '+str(self.waste_date)+', '+ str(self.waste_time))


# Курсы валют
class ExchangeRates(models.Model):
	# Курс валют для касира
	exchange_rate = models.CharField(max_length = 400)
	# Касса к которой привязан курс валют
	cashbox = models.ForeignKey(OrdinaryCashier)
	# Дата изменения курса валют
	change_date = models.DateField()
	# Время операции
	change_time = models.TimeField()

	def __str__(self):
		return ('№ ' + str(self.id) +
				'. Для кассы: '+ str(self.cashbox.cashier_description_short) +
				'; ' +str(self.change_date)+', '+ str(self.change_time))


# Операции пополнения
class IncreaseOperations(models.Model):
	# Дата операции
	operation_date = models.DateField()
	# Время операции
	operation_time = models.TimeField()
	# Данные кассы
	person_data = models.ForeignKey(OrdinaryCashier)
	# ФИО кассира проведшего операцию
	person_surname = models.CharField(max_length = 20)
	# ID операции зачисления
	increase_operation_id = models.IntegerField(default = 0)
	# ВОзможность использования валюты
	usability = models.BooleanField(default = True)

	# Курс по которому зачисленна валюта
	increase_exchange_rate = models.FloatField(default = 0)
	# Тип зачисленной валюты
	increase_currency = models.CharField(max_length = 5)
	# Зачисленная сумма
	increase_summ = models.FloatField()

	def __str__(self):
		return ('№ ' + str(self.increase_operation_id) + '. ' + str(
				self.increase_summ) + ', '+str(self.increase_currency) +
				' по ' + str(self.increase_exchange_rate) + \
				'; ' + str(self.operation_date)+', ' + str(self.operation_time))
