import sys
import requests
import time
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from collections import deque



class Tree:
    #инициализация класса Tree
    def __init__(self, parent, url, degree):
        #установить ссылку на предка
        self.parent = parent
        #установить значение вершины
        self.url = url
        #установить степень вершины
        self.degree = degree

    def setSubURLs(self):
        #если степень вершины максимальная, то искать глубже смысла нет
        if self.degree == max_degree:
            return
        #получить список ссылок на странице    
        urls = getSubURLs(self.url)
        #если целевая ссылка среди найденых на странице составляем ответ 
        if target_url in urls:
            #инициализируем список
            answer = []
            #добавляем целевую ссылку в список
            answer.append(target_url)
            #взять текущую вершину и положить в node
            node = self
            #пока у node есть предок
            while not node.parent is None:
                #добавить url из node в список
                answer.append(node.url)
                #перейти на родительскую вершину
                node = node.parent
            #добавить вершину всего дерева
            answer.append(node.url)
            #по всему перевернутому([::-1]) списку без последнего элемента ([:-1])
            for i in answer[::-1][:-1]:
                #вывод ответа без последней ссылки, sys.stdout.write а не print, потому что print переносит строку
                sys.stdout.write(i + " => ")
            #вывод последней ссылки
            sys.stdout.write(answer[0] + '\n')    
            exit(0)
        for url in urls:
            #создать вершину из ссылки, родителем будет текущая вершина, а степень равна степени текущей вершины + 1
            node = Tree(self, url, self.degree + 1)
            #добавить созданную вершину в очередь
            queue.append(node)

#проверка ссылки на корректность
def valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

#получить set() ссылок со страницы
def getSubURLs(url):
    #основу взяли тут, немного видоизменили для нашей задачи
    #https://newtechaudit.ru/izvlechenie-vseh-ssylok-veb-sajta-s-pomoshhyu-python/
    urls = set()
    #скачивает контент со ссылки и парсит
    soup = BeautifulSoup(requests.get(url).content, "html.parser")


    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            continue
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not valid_url(href):
            continue
        #если мы уже такую ссылку уже находили, то мы с ней ничего не делаем
        if href in int_url:
            continue
        #проверяем совпадает доменное имя и доменное имя ссылки
        if domain_name not in href:
            continue
        #добавить ссылку в набор
        urls.add(href)
        #добавить ссылку в глобальный набор, чтобы измежать повторного просмотра
        int_url.add(href)
    return urls

#проверяем параметры (обязательно 4 параметра, тк первый название программы main.py)
if len(sys.argv) != 4:
    print("bad params")
    exit(1)

#проверяем что 2 и 3 аргументы это ссылки
if not valid_url(sys.argv[1]):
    print("invalid start url: " + sys.argv[1])
    exit(2)
if not valid_url(sys.argv[2]):
    print("invalid target url: " + sys.argv[2])
    exit(2)

#если 2 и 3 ссылки одинаковые вернуть ответь
if sys.argv[1] == sys.argv[2]:
    print(sys.argv[1])
    exit(0)

#макс глубина дерева
max_degree = 5
#доменное имя первой ссылки сссылки, например для https://en.wikipedia.org/wiki/Six_degrees_of_separation будет en.wikipedia.org
domain_name = urlparse(sys.argv[1]).netloc
#проверяем что доменное имя первой и второй ссылки совпадает
if urlparse(sys.argv[2]).netloc != domain_name:
    print("start and target urls has different domain names")
    exit(3)

#вычисляем и проверяем rate_limit (сколько будем ждать между запросами 60/rate_limit)
try:
    rate_limit = int(sys.argv[3])
    if rate_limit < 1:
        print("rate_limit less then 1")
        exit(4)
except ValueError:
    print("invalid rate_limit")
    exit(4)

#набор ссылок которые мы уже посетили или планируем посетить (чтобы не было циклов в графе(дереве))
int_url = set()
#какую ссылку ищем
target_url = sys.argv[2]
#вершина дерева (родитель вершины None и степень 0)
tree = Tree(None, sys.argv[1], 0)
#инициализировать очерель
queue = deque()
#добавить вершину в очередь
queue.append(tree)
#пока очередь не пустая выполняем следюущее
while queue:
    #достать элемент из очереди (когда достаем элемент удаляется для очереди)
    node = queue.popleft()
    #найти потомков для вершины
    node.setSubURLs()
    #ожидание между запросами
    time.sleep(60/rate_limit)

#теперь аналогично но меняем изначальные и target ссылки местами
int_url = set()
target_url = sys.argv[1]
tree = Tree(None, sys.argv[2], 0)
queue = deque()
queue.append(tree)
while queue:
    node = queue.popleft()
    node.setSubURLs()
    time.sleep(60/rate_limit)

print("degree limit has been reached")
