import requests, re
from bs4 import BeautifulSoup


def remove_all(string):
    pattern = re.compile(r'[А-Яа-яёЁ0-9 -]+')
    return pattern.findall(string)[0].strip()


def remove_all_tab(string):
    return string.replace('\t', '').replace('\n', '')


def only_type(string):
    pattern = re.compile(r'[А-Яа-яёЁ, ]+')
    return pattern.findall(string)[0]


def only_duration(string):
    pattern = re.compile(r'[\d]{0,} ч. [\d]{0,} мин.')
    return pattern.findall(string)


def only_time(string):
    pattern = re.compile('[\d]{2}:[\d]{2}')
    return pattern.findall(string)


def karo_theaters():
    main_url = "https://karofilm.ru"
    theaters_url = "https://karofilm.ru/theatres"

    attempt = requests.get(theaters_url)

    if attempt.status_code == 200:
        pass
    else:
        print("page is unavailable")
        return

    soup = BeautifulSoup(attempt.text, "html.parser")

    theaters_list = soup.findAll("li", class_="cinemalist__cinema-item")

    dicti = {}

    for theater in theaters_list:
        id = theater["data-id"]

        name = theater.findAll("h4")[0].text

        dicti[name] = {
            'address': theater.find("div", class_="cinemalist__cinema-item__contacts").find("p").text.split('+')[0].strip(),
            'telephone': '+' + theater.find("div", class_="cinemalist__cinema-item__contacts").find("p").text.split('+')[1].strip(),
            'metro': [remove_all(i.text) for i in theater.findAll('li', class_='cinemalist__cinema-item__metro__station-list__station-item')],
        }

        karo_cinema(dicti=dicti, id=str(id), name=name)

    return dicti


def karo_cinema(dicti, id, name):
    current_url = "https://karofilm.ru/theatres?id=" + id
    attempt = requests.get(current_url)
    soup = BeautifulSoup(attempt.text, "html.parser")

    cinemas = soup.findAll('div', class_='cinema-page-item__schedule__row__data')
    cinemas_dicti = {}

    #dates = soup.find('div', class_='ik_select_list_inner')

    for cinema in cinemas:
        cinema_title = ','.join(cinema.findAll('h3')[0].text.split(',')[:-1]).strip()
        cinemas_dicti[cinema_title] = {'age': None, 'items': {}}
        cinemas_dicti[cinema_title]['age'] = cinema.findAll('h3')[0].text.split(',')[-1]
        cinema_types = cinema.findAll('div', class_='cinema-page-item__schedule__row__board-row')
        for type_ in cinema_types:
            type_name = type_.findAll('div', class_='cinema-page-item__schedule__row__board-row__left')
            for j in type_name:
                cinemas_dicti[cinema_title]['items'][j.text.strip()] = []
                current = j.text.strip()
            sessions = type_.findAll('div', class_='cinema-page-item__schedule__row__board-row__right')
            for session in sessions:
                for i in session.findAll('a', class_='karo-wi-button sessionButton'):
                    cinemas_dicti[cinema_title]['items'][current].append(i.text)

    dicti[name].update({'cinema schedule': cinemas_dicti})



def kinomax_theaters():
    main_url = "https://kinomax.ru"
    theaters_url = "https://kinomax.ru/finder"

    attempt = requests.get(theaters_url)

    if attempt.status_code == 200:
        pass
    else:
        print("page is unavailable")
        return

    soup = BeautifulSoup(attempt.text, "html.parser")

    theaters_list = soup.findAll('div', class_="pt-3 pb-3")

    dicti = {}

    for theater in theaters_list:
        id = "/" + str(theater.find('a')).split('/')[1] + "/"

        name = theater.find("a").text
        counter = 1

        dicti[name] = {
            'address': theater.find("div", class_="fs-08").text.strip().split('·')[-1].strip(),
            'metro': remove_all(theater.find("div", class_="fs-08").text.strip()) if len(remove_all(theater.find("div", class_="fs-08").text.strip())) > 0 else '-',
            'telephone': '-'
        }

        kinomax_cinema(main_url=main_url, dicti=dicti, id=str(id), name=name)
    return dicti


def kinomax_cinema(main_url, dicti, id, name):
    current_url = main_url + id
    attempt = requests.get(current_url)
    soup = BeautifulSoup(attempt.text, "html.parser")

    cinemas = soup.findAll('div', class_="d-flex border-bottom-1 border-stack film")
    cinemas_dicti = {}

    for cinema in cinemas:
        cinema_title = cinema.findAll('div', class_='w-70')[0].text.strip()
        cinemas_dicti[cinema_title] = {'age': None, 'type': None, 'duration': None, 'items': {}}
        cinemas_dicti[cinema_title]['age'] = cinema.findAll('div', class_='fs-07 film-rating')[0].text.strip()
        cinemas_dicti[cinema_title]['type'] = only_type(remove_all_tab(cinema.findAll('div', class_='d-flex fs-08 pt-3 text-main')[0].text))
        cinemas_dicti[cinema_title]['duration'] = only_duration(remove_all_tab(cinema.findAll('div', class_='d-flex fs-08 pt-3 text-main')[0].text))
        cinema_types = cinema.findAll('div', class_='d-flex w-100 schedule-row')
        for type_ in cinema_types:
            type_name = type_.find('div', class_='w-10 format-tag')
            for j in type_name:
                cinemas_dicti[cinema_title]['items'][j.strip()] = []
                current = j.strip()
            sessions = type_.findAll('div', class_='d-flex flex-wrap')
            for session in sessions:
                for i in session.findAll('div', class_='session pr-2 d-flex flex-column pb-3'):
                    cinemas_dicti[cinema_title]['items'][current].append(str(remove_all_tab(i.text)[:5] + ' ' + remove_all_tab(i.text)[5:]))

    #dicti.update({'date': None})
    dicti[name].update({'cinema schedule': cinemas_dicti})


def luxor_theaters():
    main_url = "https://www.luxorfilm.ru"
    theaters_url = main_url + '/cinema/'

    attempt = requests.get(theaters_url)

    if attempt.status_code == 200:
        pass
    else:
        print("page is unavailable")
        return

    soup = BeautifulSoup(attempt.text, "html.parser")

    theaters_list = soup.findAll('div', class_="cinema-item")

    dicti = {}

    for theater in theaters_list:
        id = theaters_url + str(theater.find('a', class_='cinema-item-link')['href'])

        name = theater.find("a", class_='cinema-item-link').text

        dicti[name] = {
            'address': theater.find('a')['address'],
            'metro': theaters_url + str(theater.find('a', class_='cinema-now')['href']),
        }

        luxor_cinema(dicti=dicti, id=str(id), name=name)

    a = luxor_theaters()
    for i in dicti:
        ans = str(i, dicti[i]['cinema schedule'])

    return dicti



def luxor_cinema(dicti, id, name):
    current_url = id
    attempt = requests.get(current_url)
    soup = BeautifulSoup(attempt.text, "html.parser")

    cinemas = soup.findAll('tr', class_="one-film-line")
    cinemas_dicti = {}

    for cinema in cinemas:
        cinema_title = cinema.findAll('h3')[0].text.strip()
        cinemas_dicti[cinema_title] = []
        sessions = cinema.findAll('div', class_='d-right')
        for i in sessions:
            time = only_time(i.find('a').text)
            try:
                a = time[0]
            except:
                time = None
            price = i.find('tbody').findAll('td')[-1].text
            hall = i.find('tbody').findAll('td')[0].text
            if time is not None:
                session = str(time[0] + ', ' + price + ', ' + hall)
                cinemas_dicti[cinema_title].append(session)

    #dicti.update({'date': None})
    dicti[name].update({'cinema schedule': cinemas_dicti})




