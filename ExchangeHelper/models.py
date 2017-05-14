from django.db import models
from django.contrib.auth.models import User


# Создание рядовойго кассира
class OrdinaryCashier(models.Model):# Логин кассира
	user = models.ForeignKey(User)
	# ПОлное описание кассы
	cashier_description_full = models.CharField(max_length = 600)
	# Краткое описание кассы
	cashier_description_short = models.CharField(max_length = 100)

	def __str__(self):
		return self.cashier_description_short


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
	# 'currency_get': 'summ',
	# 'currency_put': 'summ'
	# }
	currency_changes = models.CharField(max_length = 20)

	# Коментарий к событию
	comment = models.CharField(max_length = 200)

	def __str__(self):
		return self.action_type


# Записки для односторонней связи кассир->админ и для записей трат администратора
class AdministratorCashCosts(models.Model):
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
		return self.waste_reason


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