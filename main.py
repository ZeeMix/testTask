from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import pymorphy2

class Parser:
    def __init__(self, keyword):
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)
        self.keyword = keyword
        self.url = f'https://dzen.ru/search?query={self.keyword}&type_filter=article%2Cbrief'
        self.word_count = {}  # Словарь с символами и их повторами

    def get_page(self):
        self.driver = webdriver.Chrome()
        self.driver.get(self.url)
        self.scroll_full_info()
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    def scroll_full_info(self):
        len_page = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);"
                                              "var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match = False
        while not match:
            last_count = len_page
            time.sleep(1)
            len_page = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);"
                                                  "var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            if last_count == len_page:
                match = True

    def find_articles(self):
        self.age_link = {}

        teg_age = "zen-ui-common-layer-meta _type_card _is-compact"
        teg_link = "card-image-compact-view__clickable"

        block_article = self.soup.findAll("div", {'class': "feed__row _items-count_1"})
        for block in block_article:
            age = block.find("div", {"class": teg_age})
            link = block.find("a", {"class": teg_link})
            # Отбор по давности статьи
            if link and age:
                for var in ['сек', 'мин', 'час', 'дн', 'ден', 'недел']:
                    if var in age.contents[0]:
                        self.age_link[link['href']] = age.contents[0]
                        break

        # for age, link in zip(self.soup.findAll("div", {"class": teg_age}),
        #                      self.soup.findAll("a", {"class": teg_link})):
        #     # Отбор по давности статьи
        #     for var in ['сек', 'мин', 'час', 'дн', 'ден', 'недел']:
        #         if var in age.contents[0]:
        #             self.age_link[link['href']] = age.contents[0]
        #             print(age.contents[0], link['href'])
        #             break
        print(f'{len(self.age_link)} - кол-во статей')

    def pars_article(self):
        self.text = []
        for article in self.age_link:
            driver = webdriver.Chrome()
            driver.get(article)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            text = soup.findAll("p", {"class": 'block__block-3c'})
            if len(text) > 1:
                span = text[1].findAll("span")
                if span:
                    for s in span:
                        self.text.extend(s.text.split())

    def counting_words(self, text: str):
        for word in text.split():
            word = word.lower()
            if len(word) > 2:
                if self.word_count.get(word):
                    self.word_count[word] = self.word_count.get(word) + 1
                else:
                    self.word_count[word] = 1

    def sort_dict(self):
        self.returned_dict = {}
        for word in self.word_count:
            count = self.word_count[word]
            if self.returned_dict.get(count):
                self.returned_dict[count].append(word)
            else:
                self.returned_dict[count] = [word]

        count = sorted(list(self.returned_dict.keys()), reverse=True)

        self.sort_dict = {}
        for c in count:
            self.sort_dict[c] = self.returned_dict[c]


        self.result_list = []

        for count in self.sort_dict:
            for word in self.sort_dict[count]:
                if len(self.result_list) < 50:
                    print(word, count)
                    self.result_list.append(word)
                else:
                    break

    def words_cloud(self):
        # Импортируем библиотеку для визуализации
        import matplotlib.pyplot as plt
        from wordcloud import WordCloud
        from stop_words import get_stop_words

        # Функция для визуализации облака слов
        def plot_cloud(wordcloud):
            # Устанавливаем размер картинки
            plt.figure(figsize=(40, 30))
            # Показать изображение
            plt.imshow(wordcloud)
            # Без подписей на осях
            plt.axis("off")

        # Записываем в переменную стоп-слова русского языка
        STOPWORDS_RU = get_stop_words('russian')

        # инициализируем лемматайзер MorphAnalyzer()
        lemmatizer = pymorphy2.MorphAnalyzer()

        # функция для лемматизации текста, на вхд принимает список токенов
        def lemmatize_text(tokens):
            # создаем переменную для хранения преобразованного текста
            text_new = ''
            # для каждого токена в тексте
            for word in tokens:
                # с помощью лемматайзера получаем основную форму
                word = lemmatizer.parse(word)
                print(word)
                print(word[0].normal_form)
                # добавляем полученную лемму в переменную с преобразованным текстом
                if len(word[0].normal_form) > 1:
                    text_new = text_new + ' ' + word[0].normal_form
            # возвращаем преобразованный текст
            return text_new

        # вызываем функцию лемматизации для списка токенов исходного текста
        self.text = lemmatize_text(self.text)

        # Генерируем облако слов
        wordcloud = WordCloud(max_words=50,
                              width=2000,
                              height=1500,
                              random_state=1,
                              background_color='black',
                              margin=20,
                              colormap='Pastel1',
                              collocations=False,
                              stopwords=STOPWORDS_RU).generate(self.text)

        # Рисуем картинку
        plot_cloud(wordcloud)

        plt.ioff()
        plt.show()
        wordcloud.to_file('hp_cloud_simple.png')

    def start(self):
        self.get_page()
        self.find_articles()
        self.pars_article()
        self.sort_dict()


if __name__ == "__main__":
    start_time = time.perf_counter()
    pars = Parser('игра')
    pars.start()
    pars.words_cloud()
    end_time = time.perf_counter()
    print(end_time - start_time)