from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Запустить Chrome без окна (headless режим)

# Инициализация WebDriver
driver = webdriver.Chrome(options=options)

# Запрос к странице
url = 'https://tap.az/'
driver.get(url)

# Получение HTML содержимого страницы
html_content = driver.page_source
print(html_content)

# Закрытие браузера
driver.quit()
