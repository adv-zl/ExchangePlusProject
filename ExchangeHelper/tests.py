from django.test import Client, TestCase

from .models import Group, OrdinaryCashier, User


# Тестим создание новой кассы
class OrdinaryCashierTestCase(TestCase):
	def setUp(self):
		# Группы
		self.SUPERVISOR_GRP = Group.objects.create(name = 'Supervisor')
		self.CHIEF_GRP = Group.objects.create(name = 'ChiefCashier')
		self.ORDINARY_GRP = Group.objects.create(name = 'OrdinaryCashier')
		# Тестовый юзер
		self.USER = User.objects.create(
				username = 'UnitTester',
				password = 'SuperPassword',
		)
		# Создаём кассу под юзера
		OrdinaryCashier.objects.create(
				user = self.USER,
				cashier_description_full = "Full description",
				cashier_description_short = "Short description",
		)
		self.USER.groups.add(self.ORDINARY_GRP, self.CHIEF_GRP, self.SUPERVISOR_GRP)

	# Проверяем описание кассы
	def test_cashbox_description(self):
		ordinary_info = OrdinaryCashier.objects.get(user = self.USER)
		self.assertEqual(ordinary_info.cashier_description_short, "Short description")
		self.assertEqual(ordinary_info.cashier_description_full, "Full description")

	# Проверяем, находитсмя ли человек в выбранной группе
	def test_user_groups(self):
		ordinary_info = OrdinaryCashier.objects.get(user = self.USER)
		self.assertTrue(ordinary_info.user.groups.filter(name = "OrdinaryCashier").exists())
		self.assertTrue(ordinary_info.user.groups.filter(name = "ChiefCashier").exists())
		self.assertTrue(ordinary_info.user.groups.filter(name = "Supervisor").exists())


# тестируем вход юзера и прочее
class ClientCheck(TestCase):
	def setUp(self):
		self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')
		# Группы
		self.SUPERVISOR_GRP = Group.objects.create(name = 'Supervisor')
		self.CHIEF_GRP = Group.objects.create(name = 'ChiefCashier')
		self.ORDINARY_GRP = Group.objects.create(name = 'OrdinaryCashier')
		# Тестовый юзер
		self.USER = User.objects.create(
				username = 'UnitTester',
				password = 'SuperPassword',
		)
		# Создаём кассу под юзера
		OrdinaryCashier.objects.create(
				user = self.USER,
				cashier_description_full = "Full description",
				cashier_description_short = "Short description",
		)
		# self.USER.groups.add(self.ORDINARY_GRP, self.CHIEF_GRP, self.SUPERVISOR_GRP)

	# Проверяем вход
	def test_login_user(self):
		# Проверяем корректный логин
		response = self.client.post('/login/', {'username': self.USER.username,
												'password': self.USER.password,
												'surname': 'Tester A.A.'
												}
									)
		self.assertTrue(response)

		# ПРоверяем логин с неверными данными
		response = self.client.post('/login/', {'username': 'Qwerty',
												'password': 'Pass',
												'surname': 'Tester A.A.'
												}
									)
		self.assertTrue('Неверный логин или пароль!'.encode() in response.content)

	# Проверяем доступ к страницам для залогиненных лиц
	def test_check_login_only_pages(self):
		# Доступныые всем страницы
		response = self.client.get('/home/')
		self.assertEqual(response.status_code, 200)

		response = self.client.get('/wiki/')
		self.assertEqual(response.status_code, 200)

		response = self.client.get('/login/')
		self.assertEqual(response.status_code, 200)

		response = self.client.get('/logout/')
		self.assertEqual(response.status_code, 200)
		# Доступные лишь после логина страницы
		response = self.client.get('/index/')
		self.assertEqual(response.status_code, 302)

		response = self.client.get('/view-cashbox/1')
		self.assertEqual(response.status_code, 301)

		response = self.client.get('/edit-cashbox/1')
		self.assertEqual(response.status_code, 301)

		response = self.client.get('/create-cashbox/')
		self.assertEqual(response.status_code, 302)

		response = self.client.get('/private/')
		self.assertEqual(response.status_code, 302)

		response = self.client.get('/financial-statement/')
		self.assertEqual(response.status_code, 302)

	# Проверяем доступ к страницам для ограниченного круга лиц
	def test_check_chief_only_pages(self):
		pass



