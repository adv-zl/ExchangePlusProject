import schedule
import sqlite3, os, datetime

def main():
	# TODO Организовать заупск скрипта раз в день и привязать его к дажнге или отдельным скриптом устроить
	# Изменение рабочей директории
	os.chdir('/'.join(os.getcwd().split('/')[:-2]))
	# Подключение к БД
	connection = sqlite3.connect('ExchangeHelperDB')
	cursor = connection.cursor()
	# Делаем все старые операции недоступными для удаления
	cursor.execute("""UPDATE ExchangeHelper_exchangeactions 
						SET possibility_of_operation = 0
						WHERE (operation_date < '{0}');""".format(datetime.date.today()))
	connection.commit()
	connection.close()
	print('complate')

# Запуск скрипта каждый день в 12 часов ночи и одну минуту, что бы данные за
# прошлый день схоронились
schedule.every().day.at("00:01").do(main())