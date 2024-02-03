import requests
import selenium
import re
import sqlite3
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC    
from selenium.webdriver.common.by import By
import time

login = "22200795"
pwd = "cMZCzfB2"

conn = sqlite3.connect('mydatabase.db')
c = conn.cursor()
c.execute('SELECT name FROM group_names')
names = c.fetchall()

driver = webdriver.Firefox()

driver.get("https://moodle.preco.ru/login/index.php")
driver.find_element(By.ID, "username").send_keys(login)
driver.find_element(By.ID, "password").send_keys(pwd)
driver.find_element(By.ID, "loginbtn").click()

# Получаем все номера групп из таблицы group_names
c.execute('SELECT name FROM group_names')
group_numbers = c.fetchall()


# Для каждого номера группы выполняем команду DROP TABLE IF EXISTS и CREATE TABLE
for name in names:
    group_name = name[0].replace('-', '_').replace('/', '_')
    c.execute(f'DROP TABLE IF EXISTS schedule_{group_name}')
    c.execute(f'CREATE TABLE schedule_{group_name} (date text, schedule_raw text)')
  
for name in names:
    group_name = name[0].replace('-', '_').replace('/', '_')
    driver.get("https://moodle.preco.ru/blocks/lkstudents/sheduleonline.php")
    option = driver.find_element(By.XPATH, f'//option[contains(text(), "{name[0]}")]')
    driver.execute_script("arguments[0].setAttribute('selected', '')", option)
    
    form = driver.find_element(By.ID, "id_submitbutton").click()

    # Парсинг 'urk_scheduleblock'
    schedule_blocks = driver.find_elements(By.CLASS_NAME, 'urk_sheduleblock')
    schedule_raw = [block.text for block in schedule_blocks]

    # Форматируем ячейки
    schedule_formatted = []
    for day in schedule_raw:
        day = re.sub(r'(\d{1,2}:\d{2})\n?(\d{1,2}:\d{2})', r'\1-\2', day)  # объединяем время
        day = re.sub(r'([А-Яа-я]+) ([А-Яа-я]+) ([А-Яа-я]+)', r'\1 \3', day)  # удаляем А блять
        schedule_formatted.append(day)

    # Импорт в бд
    for i, day in enumerate(schedule_formatted, 1):
        # разбиваем дни на строки и берем первую строку в качестве даты
        date = day.split('\n')[0]
        # вставляем данные в соответствующую таблицу
        c.execute(f"INSERT INTO schedule_{group_name} VALUES (?, ?)", (date, day))
# Сохраняем изменения
conn.commit()
conn.close()
driver.close()