from django.db import models


# Создание администратора касс
class ChiefCashier(models.Model):
	# Логин администратора
	chief_login = models.CharField(max_length = 30, unique = True)
	# Пароль администратора
	chief_password = models.CharField(max_length = 30)

	person_role = models.BooleanField(default = True)

	# Получаем роли
	def get_chief_role(self):
		return self.person_role


# Создание рядовойго кассира
class OrdinaryCashier(models.Model):
	# ФИО кассира
	ordinary_cashier_name = models.CharField(max_length = 20, unique = True)
	# Логин кассира
	ordinary_cashier_login = models.CharField(max_length = 30, unique = True)
	# Пароль для входа кассира
	ordinary_cashier_password = models.CharField(max_length = 30)
	# ПОлное описание кассы
	cashier_description_full = models.CharField(max_length = 600)
	# Краткое описание кассы
	cashier_description_short = models.CharField(max_length = 100)
	# Курс валют для касира
	exchange_rate = models.CharField(max_length = 200)

	# Получаем имя юзера
	def get_cashier_name(self):
		return self.ordinary_cashier_name

	# Получаем описание юзера
	def get_cashier_description(self):
		return self.cashier_description_full

	# Получаем таблицу валют
	def get_exchange_table(self):
		return self.exchange_rate


# Таблица действий юзера и учёта суммы денег
class ExchangeActions(models.Model):
	# Дата операции
	operation_date = models.DateField()
	# Время операции
	operation_time = models.TimeField()
	# Данные кассира
	person_surname = models.ForeignKey(OrdinaryCashier)
	# Действия которые были проведены при операции
	person_action = models.CharField(max_length = 200)
	# Список валют в кассе и их баланс
	money_balance = models.CharField(max_length = 200)
