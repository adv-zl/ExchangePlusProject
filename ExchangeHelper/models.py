from django.db import models
from django.contrib.auth.models import AbstractBaseUser, AbstractUser, User, UserManager


# Создание рядовойго кассира
class OrdinaryCashier(models.Model):
	# ФИО кассира
	ordinary_cashier_name = models.CharField(max_length = 20, unique = True, blank=True)
	# Логин кассира
	user = models.ForeignKey(User)
	# ПОлное описание кассы
	cashier_description_full = models.CharField(max_length = 600, blank=True)
	# Краткое описание кассы
	cashier_description_short = models.CharField(max_length = 100, blank=True)
	# Курс валют для касира
	exchange_rate = models.CharField(max_length = 200, blank=True)

	def __str__(self):
		return self.cashier_description_short
	# Получаем имя юзера
	def get_cashier_name(self):
		return self.ordinary_cashier_name

	# Получаем краткое описание юзера
	def get_cashier_short_description(self):
		return self.cashier_description_short

	# Получаем полное описание юзера
	def get_cashier_full_description(self):
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
	person_data = models.ForeignKey(OrdinaryCashier)
	# Действия которые были проведены при операции
	person_action = models.CharField(max_length = 200)
	# Список валют в кассе и их баланс
	money_balance = models.CharField(max_length = 200)
	# Коментарий к событию
	action_comment = models.CharField(max_length = 200)

	def __str__(self):
		return self.person_action
