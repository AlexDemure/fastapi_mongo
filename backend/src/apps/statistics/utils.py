import os
import pickle
import time

import bs4
import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from structlog import get_logger

from backend.src.apps.statistics.settings import FILE_PATH, GOOGLE_ACCOUNT, GOOGLE_PASSWORD, DATASTUDIO_LINK, CHROMEDRIVER_PATH
from backend.src.apps.statistics.crud import get_document_by_key
from backend.src.apps.xlsx.utils import prepare_data_from_csv_for_xlsx, write_data_to_xlsx


class GoogleDataStudio:

    logger = None
    driver = None  # Драйвер для взаимодействия с браузером.
    action_chains = None  # Объект для низкоуровневыхх действий в браузере: нажатие кнопок, движение мыши и.т.п

    path_to_download_dir = FILE_PATH + 'data_studio/'  # Директория для загрузки файлов из браузера.
    path_to_cookie_pickle = path_to_download_dir + 'cookies.pkl'

    statistic_name = 'Publisher Dashboard 2.0 (Storytel Hub - Russia Self Publishing Portal)'
    general_statistic_name = statistic_name + '_Consumption_Таблица'
    audiobook_rates_statistic_name = statistic_name + '_C20 and finishing rate_Таблица'

    def __init__(self):
        self.logger = get_logger()
        self.driver = self.initialize_browser_driver()
        self.action_chains = ActionChains(self.driver)

    def initialize_browser_driver(self) -> webdriver:
        """
        Инициализируем драйвер для работы с браузером.
        """
        options = Options()
        # options.add_argument('user-agent=Chrome/86.0.4240.75 Safari/537.36')  # Вкл. графический интерфейс браузера
        options.add_argument('--headless')  # Выкл. графический интерфейс браузера
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Указываем путь, куда будет сохраняться скачиваемые файлы
        prefs = {"download.default_directory": self.path_to_download_dir}
        options.add_experimental_option('prefs', prefs)

        driver = webdriver.Chrome(  # Объект для управления браузером.
            executable_path=CHROMEDRIVER_PATH,
            chrome_options=options
        )
        return driver

    def upload_cookies_to_browser(self) -> None:
        """
        Загружаем cookies в открытое окно браузера.
        """
        try:
            cookies = pickle.load(open(self.path_to_cookie_pickle, "rb"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        except Exception as exc:
            self.logger.debug(f'Cookie import error: {exc}')

        self.logger.debug('Cookies uploaded')

    async def authorization(self, db) -> None:
        """
        Авторизация в google data studio, через аккаунт google.
        """

        try:  # Пытаемся найти поле для ввода логина (тег: input)
            email = self.driver.find_element_by_id('identifierId')
        except NoSuchElementException:
            email = self.driver.find_element_by_id('Email')
        email.send_keys(GOOGLE_ACCOUNT)  # Вводим логин google аккаунта

        try:  # Пытаемся найти кнопку для перехода к следующему шагу авторизации
            next_ = self.driver.find_element_by_id('identifierNext')
        except NoSuchElementException:
            next_ = self.driver.find_element_by_id('next')
        next_.click()
        time.sleep(5)

        try:  # Пытаемся найти поле для ввода пароля (тег: input)
            passwd = self.driver.find_element_by_name('password')
        except NoSuchElementException:
            passwd = self.driver.find_element_by_id('password')
        passwd.send_keys(GOOGLE_PASSWORD)  # Вводим пароль google аккаунта

        try:  # Пытаемся найти кнопку для перехода к следующему шагу авторизации
            next_ = self.driver.find_element_by_id('passwordNext')
        except NoSuchElementException:
            next_ = self.driver.find_element_by_id('submit')
        next_.click()
        time.sleep(5)

        # В google data studio двух-факторная авторизация
        try:  # Пытаемся найти поле для ввода пин-кода, который придет владельцу аккаунта на телефон
            pin = self.driver.find_element_by_name('Pin')
        except NoSuchElementException:
            pin = self.driver.find_element_by_name('idvPin')

        pin_code = None
        while pin_code is None:
            # Использовать input() невозможно, т.к. код работает в демон-процессе,
            # Иначе быудет ошибка EOFError. Поэтому, пытаемся получить пин-код из MongoDB.
            # Владелец аккаунта должен его передать через API endpoint.
            pin_code = await get_document_by_key('pin_code', db)
            time.sleep(5)

        pin.send_keys(str(pin_code['pin_code']))  # Отправка PIN кода

        try:
            next_ = self.driver.find_element_by_id('idvPreregisteredPhoneNext')
        except NoSuchElementException:
            next_ = self.driver.find_element_by_id('submit')
        next_.click()
        time.sleep(5)

        self.logger.debug('Authorization to Google Data Studio successfully finished')

    async def login_to_data_studio(self, db) -> None:
        """Вход в личный кабинет google data studio."""
        self.driver.get('https://datastudio.google.com/')
        self.upload_cookies_to_browser()

        self.driver.get(DATASTUDIO_LINK)
        self.driver.maximize_window()  # Запуск. полноэкранный режим, чтобы все элементы были в зоне видимости selenium

        time.sleep(5)
        if self.driver.current_url != DATASTUDIO_LINK:  # Блок авторизации
            await self.authorization(db)
            self.driver.get(DATASTUDIO_LINK)  # data studio

        pickle.dump(self.driver.get_cookies(), open(self.path_to_cookie_pickle, "wb"))  # Сохранение куки
        self.logger.debug('Cookies updated')
        time.sleep(15)  # Ожидание прогрузки страницы

    def open_publication_date_tab(self) -> None:
        """
        Открывает вкладку Publication date.
        """

        # В google data studio динамически подгружается html, id некоторых элементов может меняться,
        # поэтому, чтобы точно найти требуемый элемент - эл. с дефолтными фильтрами.
        data_studio_html = bs4.BeautifulSoup(self.driver.page_source, features='html.parser')  # Парсим страницу
        date_options = data_studio_html.find("md-select", {"ng-model": "$ctrl.selectedDateRangeOption"})
        id_date_options = date_options.get('id')  # Получаем id элемента
        date_options_html_element = self.driver.find_element_by_id(id_date_options)  # Эл. для взаим-ия через selenium
        date_options_html_element.click()

    def choosing_date_filter_in_open_publication_date_tab(self, text_in_filter_option: str) -> None:
        """
        Выбирает одну из дефолтных google опций, внутри вкладки Publication date.

        Вкладка Publication date обязательно должна быть открыта, перед вызовом функции,
        в ином случае удет вызвано исключение ElementNotInteractableException.
        :param text_in_filter_option: Текст внутри треуемой опции.
        """

        div_options = self.driver.find_elements_by_class_name('md-text')  # div с текстом опций
        for option in div_options:
            if text_in_filter_option in option.text.strip():
                # Когда находим требуемый div, т.к. взимодействовать с ним не можем ->
                option_element_to_interact = option.find_element_by_xpath(
                    '..')  # Получаем родительский - интерактивный эл.
                option_element_to_interact.click()
                break

    def apply_date_filter_in_open_publication_date_tab(self) -> None:
        """
        Нажатие кнопки Применить, внутри вкладки Publication date.

        Вкладка Publication date обязательно должна быть открыта, перед вызовом функции,
        в ином случае удет вызвано исключение ElementNotInteractableException.
        """
        filter_table_by_dates_footer = self.driver.find_element_by_class_name('button-bar')  # Футер вкладки
        apply_button = filter_table_by_dates_footer.find_element_by_class_name("md-raised")  # Кнопка применить
        apply_button.click()

    def choosing_download_option_in_open_download_menu(self, text_in_download_option: str) -> None:
        """
        Выбирает одну из дефолтных google опций, внутри вкладки с вариантоами скачивания данных.

        Вкладка с вариантоами скачивания данных обязательно должна быть открыта, перед вызовом функции,
        в ином случае удет вызвано исключение ElementNotInteractableException.
        :param text_in_download_option: Текст внутри треуемой опции.
        """
        download_options_menu = self.driver.find_element_by_class_name('mat-menu-content')
        download_options = download_options_menu.find_elements_by_class_name('mat-focus-indicator')
        for option in download_options:
            if text_in_download_option in option.text:
                option.click()
                break

    def scroll_to_html_element(self, element: WebElement) -> None:
        """
        Скролл страницы браузера к требуемому элементу.

        Скролл осуществляется за счет запуска javascript кода.
        Экран прокручивается так, чтобы элемент находился по центру окна браузера.
        :param element: объект (html элемент) к которму необходимо проскроллить страницу.
        """
        javascript_code = 'arguments[0].scrollIntoView({block: "center", inline: "nearest"});'
        self.driver.execute_script(javascript_code, element)

    def download_general_statistics_for_one_day(self, date: datetime.date = None) -> str:
        """
        Загрузка оновного файла статистики из вкладки Consumption в google data studio.
        """

        filter_table_by_dates = self.driver.find_element_by_class_name('datepicker')  # Фильтр с выбором дат
        filter_table_by_dates.click()
        time.sleep(2)

        if date is not None:
            self.choose_specific_date(date)
        else:
            self.open_publication_date_tab()
            time.sleep(2)
            self.choosing_date_filter_in_open_publication_date_tab('Сегодня')

        self.apply_date_filter_in_open_publication_date_tab()
        time.sleep(15)

        table_header = self.driver.find_element_by_class_name('cd-5i4rh20mac-header')  # Шапка, необходимой таблицы
        self.scroll_to_html_element(table_header)  # Скролл к элементу

        download_options_button = table_header.find_element_by_tag_name('chart-menu-button')  # Меню с выбором загрузки
        download_options_button.click()
        time.sleep(2)

        self.choosing_download_option_in_open_download_menu('CSV (Excel)')
        time.sleep(17)
        self.logger.debug('General statistic file downloaded')

        csv_statistic_full_file_name = self.path_to_download_dir + self.general_statistic_name + '.csv'
        xlsx_statistic_file_name = self.path_to_download_dir + self.general_statistic_name + '.xlsx'

        if os.path.isfile(xlsx_statistic_file_name):
            os.remove(xlsx_statistic_file_name)

        data_for_xlsx = prepare_data_from_csv_for_xlsx(csv_statistic_full_file_name)
        write_data_to_xlsx(data_for_xlsx, xlsx_statistic_file_name)

        os.remove(csv_statistic_full_file_name)

        self.logger.debug('General statistics file rewritten to xlsx file')
        return xlsx_statistic_file_name

    def download_audiobook_rates_statistic_for_one_day(self, date: datetime.date = None) -> str:
        """
        Загрузка оновного файла статистики из вкладки  C20 and finishing rate в google data studio.
        """

        # В google data studio динамически подгружается html, id некоторых элементов может меняться,
        # поэтому, чтобы точно найти требуемый элемент - вкладка к статистике C20 / C25
        data_studio_html = bs4.BeautifulSoup(self.driver.page_source, features='html.parser')  # Парсим страницу
        audiobook_rates_statistic_tab = data_studio_html.find("xap-nav-link", {"aria-label": "C20 and finishing rate"})
        tab_id = audiobook_rates_statistic_tab.get('id')  # Получаем id элемента
        tab_html_element = self.driver.find_element_by_id(tab_id)  # Находим эл. для взаим-ия через selenium
        tab_html_element.click()
        time.sleep(2)

        # В текущей вкладке у элементов, нет идентификаторов, по которым можно точечно найти элемент,
        # поэтому находим все вкладки с фильтрами по датам
        date_options_tabs_list = self.driver.find_elements_by_class_name('datepicker')  # Список всех вкладок
        date_options_tab = date_options_tabs_list[-1]

        # В google data studio только вкладка "Publication date" не полностью интерактивна, т.е. центр-я часть кнопки
        # не может быть нажата / "Кликнута" => находим единственный интерактивный элемент вкладки - "▼".
        # Если нажать на всю вкладку, получим исключение ElementClickInterceptedException.
        date_options_dropdown_arrow = date_options_tab.find_element_by_class_name('dropdown-arrow')  # Элемент ▼

        # Вкладка "Publication date" находится вне зоны экрана (его не видно), поэтому, если попытаться на нее кликнуть,
        # selenium поднимет искл. ElementClickInterceptedException. Чтобы этого збежать, необходимо сделать скролл вниз
        # В метод execute_script передаем строку с кодом JavaScript.
        # driver.execute_script("arguments[0].scrollIntoView(false);", date_options_dropdown_arrow)  # Скролл вниз
        self.scroll_to_html_element(date_options_dropdown_arrow)  # Скролл к элементу
        date_options_dropdown_arrow.click()
        time.sleep(2)

        if date is not None:
            self.choose_specific_date(date)
        else:
            self.open_publication_date_tab()
            time.sleep(3)
            self.choosing_date_filter_in_open_publication_date_tab('Сегодня')

        self.apply_date_filter_in_open_publication_date_tab()
        time.sleep(15)

        table_header = self.driver.find_element_by_class_name('cd-xz2zfqpugc-header')  # Шапка, необходимой таблицы

        self.scroll_to_html_element(table_header)  # Скролл к элементу

        download_options_button = table_header.find_element_by_tag_name('chart-menu-button')  # Меню с выбором загрузки
        download_options_button.click()
        time.sleep(2)

        self.choosing_download_option_in_open_download_menu('CSV (Excel)')
        time.sleep(17)
        self.logger.debug('Audiobook rates statistic file downloaded')

        csv_statistic_full_file_name = self.path_to_download_dir + self.audiobook_rates_statistic_name + '.csv'
        xlsx_statistic_file_name = self.path_to_download_dir + self.audiobook_rates_statistic_name + '.xlsx'

        if os.path.isfile(xlsx_statistic_file_name):
            os.remove(xlsx_statistic_file_name)

        data_for_xlsx = prepare_data_from_csv_for_xlsx(csv_statistic_full_file_name)
        write_data_to_xlsx(data_for_xlsx, xlsx_statistic_file_name)

        os.remove(csv_statistic_full_file_name)

        self.logger.debug('Audiobook rates statistics file rewritten to xlsx file')
        return xlsx_statistic_file_name

    def get_week_and_every_day_of_this_week(self, list_of_weeks: list) -> tuple:
        """
        Генератор. Получаем веб-элемент недели и каждого ее дня из списка недеь.

        Вкладка Publication date обязательно должна быть открыта, перед вызовом функции,
        в ином случае удет вызвано исключение ElementNotInteractableException.
        :param list_of_weeks: Список веб-элементов (недель), полученных в открытой вкладке Publication date.
        :return Кортеж, где 1-й элемента - Номер недели (int), 2-й элемент - Номер дня (int),
        3-й элемент - веб-элемент/день для ваимодействия (объект selenium)
        """

        for week_number, week in enumerate(list_of_weeks, start=1):
            days_in_week = week.find_all("td", {"ng-repeat": "dt in row"})  # Получаем список дней в неделе.
            for day in days_in_week:
                # Т.к. в итерируемом списке, каждый элемент -> объект bs4
                day_id = day.get('id')  # Получаем id элемента
                html_day_el = self.driver.find_element_by_id(day_id)  # Получаем объект selenium
                selected_day_number = int(html_day_el.text)  # Выбранный день из опций
                yield week_number, selected_day_number, html_day_el

    def choose_specific_date(self, date: datetime.date):
        """
        Выбор конкретной даты, внутри вкладки Publication date.

        Вкладка Publication date обязательно должна быть открыта, перед вызовом функции,
        в ином случае удет вызвано исключение ElementNotInteractableException.
        :param date: Текст внутри треуемой опции.
        """

        dates_tables = self.driver.find_elements_by_class_name('uib-daypicker')  # Таблицы с датами

        for dates_table in dates_tables:

            # У таблиц нет id и с каждой новой открытой вкладкой -> html обновляется,
            # единственный способ идентифицировать таблицы и их элементы, знач. аттр. aria-labelledby
            table_attr_aria_labelledby = dates_table.get_attribute('aria-labelledby')  # Получем знач. треб-го аттр.
            # Кнопка внутри тиблицы с датами, открывает таблицу с выбором года и месяца.
            date_selection_button = dates_table.find_element_by_id(table_attr_aria_labelledby)
            date_selection_button.click()
            time.sleep(2)

            # Т.к. у таблиц нет id, сканируем весь html в поиске открывшейся таблицы "с выбором месяца и года"
            month_and_year_table = self.driver.find_element_by_class_name('uib-monthpicker')
            year_selection_button = month_and_year_table.find_element_by_id(table_attr_aria_labelledby)  # Выбор года

            selected_year = int(year_selection_button.text)  # Получаем значение года, который уже выбран в таблице.
            if selected_year != date.year:  # Если выбранный год не равен тому, который требуется
                if selected_year > date.year:  # В случае, если выбранный год больше, требуемого
                    # Находим кнопку, для выбора предыдущего года
                    change_year_button = month_and_year_table.find_element_by_class_name('uib-left')
                else:
                    # Находим кнопку, для выбора следующего года
                    change_year_button = month_and_year_table.find_element_by_class_name('uib-right')
                change_year_button.click()
                time.sleep(2)

            # Тело таблицы "с выбором года и месяца", в котором перечислены месяца
            table_body_with_months = month_and_year_table.find_element_by_tag_name('tbody')
            months_buttons = table_body_with_months.find_elements_by_tag_name('button')  # Все месяца, каждый эл. - btn
            for month_button in months_buttons:
                selected_month = month_button.text.lower()  # Выбранный месяц из опций -> англ. название месяца
                required_month = date.strftime('%B').lower()  # Из треб. даты, получаем месяц -> англ. название месяца
                if selected_month == required_month:
                    month_button.click()
                    break
            time.sleep(2)

            # Т.к. после выбора года и месяца, html поменялся, заново парсим страницу.
            # Находим нужную нам таблицу по аттр. и получаем все недели, которые в ней указаны.
            data_studio_html = bs4.BeautifulSoup(self.driver.page_source, features='html.parser')
            dates_table = data_studio_html.find("table", {"aria-labelledby": table_attr_aria_labelledby})
            weeks = dates_table.find_all("tr", {"class": "uib-weeks"})[:5]  # Получаем список из 5 недель

            for week_number, selected_day_number, day_el in self.get_week_and_every_day_of_this_week(weeks):
                # Открытая таблица с датами имеет формат календаря =>
                # В первой неделе могут быть даты из предыдущего месяца, в последней неделе из следующего =>
                # Некоторые даты, могу встретиться дважды. Поэтому, необходимо проверить:
                # Если в первой неделе есть даты с 21 по 31, не выбираем их, т.к. они из предыдущего месяца.
                if week_number == 1 and selected_day_number in [x for x in range(21, 32)]:
                    continue
                # Если в последней неделе есть даты с 1 по 7, не выбираем их, т.к. они из следующего месяца.
                elif week_number == 5 and selected_day_number in [x for x in range(1, 8)]:
                    continue

                if selected_day_number == date.day:
                    day_el.click()
                    break

            time.sleep(10)
