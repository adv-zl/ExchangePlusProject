from django.db import models
from django.contrib.auth.models import AbstractBaseUser, AbstractUser, User, UserManager


# Создание рядовойго кассира
class OrdinaryCashier(models.Model):# Логин кассира
	user = models.ForeignKey(User)
	# ПОлное описание кассы
	cashier_description_full = models.CharField(max_length = 600)
	# Краткое описание кассы
	cashier_description_short = models.CharField(max_length = 100)
	# Курс валют для касира
	exchange_rate = models.CharField(max_length = 400)

	def __str__(self):
		return self.cashier_description_short

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
	# Данные кассы
	person_data = models.ForeignKey(OrdinaryCashier)
	# ФИО кассира проведшего операцию
	person_surname = models.CharField(max_length = 20)
	# Список валют в кассе и их баланс
	money_balance = models.CharField(max_length = 200)
	# Коментарий к событию
	# {'action': 'событие типа "Инкасация/Обмен/Пополнение"',
	# 'changes': {'название валюты': %число на которое изменение было%}
	# 'comment': 'комментарий к действию од админа'}
	action = models.CharField(max_length = 200)
