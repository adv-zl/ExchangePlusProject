from selenium import webdriver
import unittest


class TestPrimaryFunctions(unittest.TestCase):
	# Первоначальная настройка и вход
	def setUp(self):
		self.browser = webdriver.Chrome()
		self.browser.implicitly_wait(30)

		self.SURNAME = 'Иванов'
		self.ADMIN_USERNAME = 'SuperUser'
		self.VISOR_USERNAME = 'SuperUser2'
		self.ORDINARY_USERNAME = 'Test_User2'
		self.PASSWORD = 'HardPassword'

	def tearDown(self):
		self.browser.quit()

	# Проверка входа для обычного юзера
	def test_ordinary_user_login(self):
		self.assertTrue(self.login(self.ORDINARY_USERNAME))
		# Проверяем доступные обычному юзеру страницы
		self.browser.get('http://127.0.0.1:8000/home/')
		assert 'http://127.0.0.1:8000/home/' in self.browser.current_url
		self.browser.get('http://127.0.0.1:8000/wiki/')
		assert 'http://127.0.0.1:8000/wiki/' in self.browser.current_url
		# Проверяем, не доступны ли ему страницы для администратора
		self.browser.get('http://127.0.0.1:8000/private/')
		assert 'http://127.0.0.1:8000/private/' not in self.browser.current_url
		self.browser.get('http://127.0.0.1:8000/financial-statement/')
		assert 'http://127.0.0.1:8000/financial-statement/' not in self.browser.current_url
		self.browser.get('http://127.0.0.1:8000/cashbox-monitoring/')
		assert 'http://127.0.0.1:8000/cashbox-monitoring/' not in self.browser.current_url
		self.browser.get('http://127.0.0.1:8000/edit-cashbox/1')
		assert 'http://127.0.0.1:8000/edit-cashbox/1' not in self.browser.current_url
		self.browser.get('http://127.0.0.1:8000/create-cashbox/')
		assert 'http://127.0.0.1:8000/create-cashbox/' not in self.browser.current_url
		# Выход
		self.assertTrue(self.log_out())

	# Проверка входа для обычного юзера
	def test_administrator_login(self):
		self.assertTrue(self.login(self.ADMIN_USERNAME))

		self.browser.get('http://127.0.0.1:8000/home/')
		assert 'http://127.0.0.1:8000/home/' in self.browser.current_url
		self.browser.get('http://127.0.0.1:8000/wiki/')
		assert 'http://127.0.0.1:8000/wiki/' in self.browser.current_url
		self.browser.get('http://127.0.0.1:8000/private/')
		assert 'http://127.0.0.1:8000/private/' in self.browser.current_url
		self.browser.get('http://127.0.0.1:8000/financial-statement/')
		assert 'http://127.0.0.1:8000/financial-statement/' in self.browser.current_url
		self.browser.get('http://127.0.0.1:8000/cashbox-monitoring/')
		assert 'http://127.0.0.1:8000/cashbox-monitoring/' in self.browser.current_url
		self.browser.get('http://127.0.0.1:8000/edit-cashbox/1')
		assert 'http://127.0.0.1:8000/edit-cashbox/1' in self.browser.current_url
		self.browser.get('http://127.0.0.1:8000/create-cashbox/')
		assert 'http://127.0.0.1:8000/create-cashbox/' in self.browser.current_url
		# Выход
		self.assertTrue(self.log_out())

	# Проверка входа для обычного юзера
	def test_visor_login(self):
		self.assertTrue(self.login(self.VISOR_USERNAME))

		self.browser.get('http://127.0.0.1:8000/home/')
		assert 'http://127.0.0.1:8000/home/' in self.browser.current_url
		self.browser.get('http://127.0.0.1:8000/wiki/')
		assert 'http://127.0.0.1:8000/wiki/' in self.browser.current_url
		self.browser.get('http://127.0.0.1:8000/private/')
		assert 'http://127.0.0.1:8000/private/' in self.browser.current_url
		self.browser.get('http://127.0.0.1:8000/financial-statement/')
		assert 'http://127.0.0.1:8000/financial-statement/' in self.browser.current_url
		self.browser.get('http://127.0.0.1:8000/cashbox-monitoring/')
		assert 'http://127.0.0.1:8000/cashbox-monitoring/' in self.browser.current_url
		self.browser.get('http://127.0.0.1:8000/edit-cashbox/1')
		assert 'http://127.0.0.1:8000/edit-cashbox/1' not in self.browser.current_url
		self.browser.get('http://127.0.0.1:8000/create-cashbox/')
		assert 'http://127.0.0.1:8000/create-cashbox/' not in self.browser.current_url
		# Выход
		self.assertTrue(self.log_out())

	# Проверка прав которыми обладает администратор, налчие элементов
	def test_administrator_privileges(self):
		self.assertTrue(self.login(self.ADMIN_USERNAME))
		# Кнопка для создания кассы
		self.assertTrue(self.browser.find_element_by_xpath('/html/body/div[2]/div/div/div[1]/ul/a/button'))
		# Список всех касс на странице
		self.assertTrue(self.browser.find_element_by_xpath('/html/body/div[2]/div/div/div[2]/div[2]/h4/b'))
		# Личный кабинет
		self.assertTrue(self.browser.find_element_by_xpath('//*[@id="bs-example-navbar-collapse-1"]/ul[1]/li[1]/a'))
		# Меню списка всех касс
		self.assertTrue(self.browser.find_element_by_xpath('//*[@id="bs-example-navbar-collapse-1"]/ul[1]/li[2]/a'))
		# Окно мониторинга
		self.assertTrue(self.browser.find_element_by_xpath('//*[@id="bs-example-navbar-collapse-1"]/ul[5]/a/button'))
		# Окно отчёта
		self.assertTrue(self.browser.find_element_by_xpath('//*[@id="bs-example-navbar-collapse-1"]/ul[4]/a/button'))
		# Выход
		self.assertTrue(self.log_out())

	# проверка прав которые имеет кассир на отображение элементов
	def test_ordinary_privileges(self):
		self.assertTrue(self.login(self.ORDINARY_USERNAME))

		self.assertTrue(self.browser.find_element_by_xpath('/html/body/div[2]/div/div/div[1]/div/div/div'))
		self.assertTrue(self.browser.find_element_by_xpath('/html/body/div[2]/div/div/div[2]/div[2]/div'))
		self.assertTrue(self.browser.find_element_by_xpath('/html/body/div[2]/div/div/div[2]/div[2]/div/a/button'))

		self.assertTrue(self.log_out())

	# Вход юзера
	def login(self, username):
		self.browser.get('http://127.0.0.1:8000/login')
		self.browser.find_element_by_name('surname').send_keys(self.SURNAME)
		self.browser.find_element_by_name('username').send_keys(username)
		self.browser.find_element_by_name('password').send_keys(self.PASSWORD)
		self.browser.find_element_by_xpath('/html/body/div[2]/div/div[2]/form/p/input').submit()
		# Проверяем, выполнены ли вход
		if 'http://127.0.0.1:8000/index/' in self.browser.current_url:
			return True
		else:
			return False

	# Выход
	def log_out(self):
		self.browser.get('http://127.0.0.1:8000/logout')
		if self.browser.find_element_by_xpath('/html/body/div[2]/h3/strong'):
			return True
		else:
			return False


if __name__ == '__main__':
	unittest.main(warnings = 'ignore')
