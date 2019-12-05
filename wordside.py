import re
import os
import string
import functools
from itertools import product
import pymorphy2
morph = pymorphy2.MorphAnalyzer()

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
cities = os.path.join(THIS_FOLDER, 'opencity.txt')    # opencity - файл содержащий список городов

def modifier(words, type):
    """Функция получает набор данных от пользователя, чистит данные от лишних символов и выводит список строк по слову в строке.
    Параметр type содержит информацию о том, какие символы удалять.
    Тип удаляемых символов передаётся в переменную type без пробелов в виде 'quotesplusprepconj'

    """
    marks = ''
    result = []
    if 'punct' in type:                               # Удаление всех знаков пунктуации
        marks += string.punctuation + '\r'
    if 'quotes' in type:                              # Удаление всех видов кавычек
        marks += '[“”‘«»„“]'
    if 'exclamation_mark' in type:                    # Удаление восклицательных знаков
        marks += '!'
    if 'space' in type:                               # Удаление пробелов и знаков табуляции
        marks += '   '
    if 'plus' in type:                                #Удаление знаков плюс
        marks += '+'
    if 'minus' in type:                               #Удаление знаков минус
        marks += '-'
    if 'prep' in type:                                # Удаление предлогов
        for word in words.strip().split(' '):
            if morph.parse(word)[0].tag.POS == 'PREP':
                words.replace(word, '')
    if 'npro' in type:                                # Удаление местоимений-существительных
        for word in words.strip().split(' '):
            if morph.parse(word)[0].tag.POS == 'NPRO':
                words.replace(word, '')
    if 'conj' in type:                                # Удаление союзов
        for word in words.strip().split(' '):
            if morph.parse(word)[0].tag.POS == 'CONJ':
                words.replace(word, '')
    if 'prcl' in type:                                # Удаление частиц
        for word in words.strip().split(' '):
            if morph.parse(word)[0].tag.POS == 'PRCL':
                words.replace(word, '')
    if 'intj' in type:                                # Удаление междометий
        for word in words.strip().split(' '):
            if morph.parse(word)[0].tag.POS == 'INTJ':
                words.replace(word, '')

    if marks != '':
        words = re.sub('[{}]'.format(re.escape(marks)), '', words) # Удаление символов
    else:
        return 'Введите тип удаляемых символов'
    words = list(words.lower().split(' '))
    if words[-1] == '':
        words.remove(words[-1])
    if 'pass' in type:                                # Удаление пустых строк
        while '' in words:
            words.remove('')
    if 'dub' in type:                                 # Удаление дублирующихся слов
        list(set(words))
    if 'decl' in type:                                # Удаление дублирующихся слов и склонений
        while len(words) > 0:
            result.append(words[0])
            words = list(set(words) - set(declension(words[0]).split('\n')))
    return words


def declension(userinput):
    """Функция получает одно или несколько слов ивозвращает список склонений заданных слов.

    """
    result = []
    decls = []
    userinput = modifier(userinput, 'punct') 
    for word in userinput:
        words = morph.parse(word)[0].lexeme        # Получение списка склонений
        for element in words:                      # Отчистка от лишних данных
            decl = str(element).split(' ')
            if len(decl[-3].replace("'", '').replace(',', '')) > 2:
                decls.append(decl[-3].replace("'", '').replace(',', ''))
        if word not in decls:                      # Проверка наличие изначальной формы в результирующем списке
            decls.append(word)
        """for i in range(len(decls)):
            if len(decls[i]) > 2:
                decls.append(decls.pop(i))"""
        result.append(decls)
        decls = []
    return result


def counter(words, deldub = False, deldecl = False):
    """Функция считает количество слов.
    Возвращает список, в котором первый элемент - количество слов, второй - все слова через пробел.
    Если передать переменной deldub значение True, будут удалены повторяющиеся слова,
    если передать переменной decl значение True, так-же будут удалены повторяющиеся склонения слов.
    
    """
    if deldub == False:
        words = modifier(words, 'punct')
    elif deldub == True and deldecl == False:
        words = modifier(words, 'punctdub')
    elif deldecl == True:
        words = modifier(words, 'punctdecl')
    return words.insert(0, 'Количество слов - ' + str(len(result)))


def generator(words):
    """Функция получает на вход несколько списков слов в фотмате списка списков, и выводит список сочетаний эллементов входных списков.

    """
    result = []
    while [] in words:
        words.remove([])
    genwords = list(product(*words))          # Создание списка сочетаний
    for i in genwords:
        result.append(' '.join(i))            # Преобразование множества в строку
    return result


def lemma(words):
    """Функция получает строку, разбивает её на список по словам и выводит список нормальных форм слов.

    """
    words = modifier(words, 'punct')
    for i in words:
        words[words.index(i)] = morph.parse(i)[0].normal_form   
    return words


def cityremover(text, stopcity = cities):
    """Функция получает текст, отчищает его от знаков пунктуации и удаляет из него города
    """
    words = modifier(text, 'punct')
    words = [word for word in words if word not in stopcity]
    words = ' '.join(words)
    return words


def trimutm(url):
    """Функция получает ссылку или несколько ссыло разделённых переносом строки(\n) и удаляет из неё utm метки.

    """
    url = url.split('\n')
    while '' in url:
        url.remove('')
    while '\r' in url:
        url.remove('\r')
    result = []
    for url in url:
        if "utm_" not in url:          # Проверка на содержание гtm метки
           result.append(url)
           continue
        matches = re.findall('(.+\?)([^#]*)(.*)', url)
        if len(matches) == 0:
           result.append(url)
           continue
        match = matches[0]
        query = match[1]
        sanitized_query = '&'.join([p for p in query.split('&') if not p.startswith('utm_')])   # Отчистка от метки
        result.append(match[0]+sanitized_query+match[2])
    return result


def crossminus(userinput):
    """ Функция получает на вход строку состоящую из списка фраз разделённых переносом строки и производит добавление слов с префиксом '-' не входящих в данную фразу,
        но входящих в стальные фразы.
        Основное предназначение - создание ключевых фраз для рекламных кампаний
    """
    words = []
    allwords = []
    result = []
    for keys in userinput.split('\n'):                # Преобразование входной строки в список списков слов
        keys = modifier(keys, 'punct')
        words.append(keys)
    dub = set(functools.reduce(set.__and__, (set(i) for i in words)))  # Определение слов повторяющихся во всех фразах
    for key in words:
        allwords += key
    allwords = set(allwords)
    allwords ^= dub
    for key in words:
        for word in allwords:
            if word not in key:
                key.append('-' + word)
    for i in range(len(words)):
        result.append(' '.join(words[i]))
    return result