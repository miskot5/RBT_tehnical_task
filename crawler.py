import requests
from bs4 import BeautifulSoup
import re
import Real_estate
import Location

pattern_elevator = r"(L|l)ift"
pattern_kuca = r"\b(K|k)u(ć|c)a\b"
pattern_stan = r"\b(S|s)tan\b"
pattern_zgrada = r"(Z|z)grada"
pattern_garage = r"(G|g)ara(ž|z)a"
pattern_parking = r"(P|p)arking"
pattern_build = r"(G|g)radjevin"
pattern_gars = r"(G|g)arsonjera"
pattertn_sports = r"(S|s)port"
pattern_lokal = r"(L|l)okal"
pattern_other = re.compile(r'\b(?:(T|t)erasa|(L|l)o(dj|đ)a|(B|b)alkon)\b', re.IGNORECASE)
pattern_work = r"(P|p)oslovni"

baseURL = 'https://www.nekretnine.rs'
def processing_home_page(URL):
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = []
    all = soup.find_all('a', text='Pogledajte sve')
    for href in all:
        all_href = href['href']

    premium_offers = soup.select('.premium-offers-item')
    for offer in premium_offers:
        href = offer.find('a', href=True)
        item_link = href['href'][1:]
        links.append(item_link)

    return links, baseURL+all_href

def finds_real_estate_links(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = []
    offers = soup.select('.offer-body')
    for offer in offers:
        href = offer.find('a', href=True)
        item_link = href['href'][1:]
        links.append(item_link)

    return links

def find_links_recursive(url, limit: int,visited_links=None):
    if visited_links is None:
        visited_links = set()

    if url in visited_links:
        return visited_links

    visited_links.add(url)
    print(url)

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    next_links = soup.find_all("a", class_="next-number")


    for next_link in next_links:
        next_url = baseURL+next_link["href"]
        if  len(visited_links) <= limit:
            find_links_recursive(next_url, limit,visited_links)

    return visited_links

#ako nismo u html reprezentaciji nasli odredjeni podatak, svakako zelimo da imamo podatak o tome u mapi, da bismo u bazi mogli to da cuvamo kao null
def map_processing(key, map):
    if key not in map:
        map[key] = None
    else:
        return map[key]

def string_to_int_processing(attribute_string, string):
    if attribute_string == string:
        return None
    else:
        result = re.sub(r'\D', '', str(attribute_string))
        if result == '':
            return None
        else:
            return int(result)

def location_processing(name,city,map):
    try:
        map[name] = city
    except KeyError:
        map[name] = None

#za izvlacenje uuid linka nekretnine
def extract_text_between_last_slashes(text):
    last_slash_index = text.rfind("/")

    if last_slash_index != -1:
        second_last_slash_index = text.rfind("/", 0, last_slash_index)

        if second_last_slash_index != -1:
            extracted_text = text[
                             second_last_slash_index + 1: last_slash_index]
            return extracted_text

    return None

def real_estate_processing(link):
    external_id = extract_text_between_last_slashes(link)
    resp = requests.get(link)
    soup = BeautifulSoup(resp.text, 'html.parser')
    infos_soup = soup.select('.property__amenities > ul > li')

    registration = False
    elevator = False
    parking = False
    other = False
    informations = {}
    for info in infos_soup:
        information = re.sub('\s{2,}','',info.text)
        separator = ':'

        if separator in information:
            separator_position = information.index(separator)
            informations[information[:separator_position]] = information[separator_position + 1:]
        if separator not in information:

            if re.search(pattern_elevator, information):
                elevator = True
            if re.search(pattern_other, information):
                other = True
            if re.search(pattern_garage, information) or re.search(pattern_parking, information):
                parking = True

    location_soup = soup.select(".stickyBox__Location")
    for loc in location_soup:
        try:
            city =re.sub(r'\s+', ' ', loc.text.split(",")[0])
            part_of_city = re.sub(r'\s+', ' ', loc.text.split(",")[1])
            location = Location.Location(city, part_of_city)
        except IndexError:
            part_of_city = None
            location = Location.Location(city, part_of_city)
        informations["Lokacija"] =  location
    type_of_real_estate = 'Nepoznato'

    if re.search(pattern_kuca, informations['Kategorija']):
        type_of_real_estate = 'Kuca' + ',' + informations['Kategorija']

    if re.search(pattern_stan, informations['Kategorija']) or re.search(pattern_gars, informations['Kategorija']):
        type_of_real_estate = 'Stan'+',' + informations['Kategorija']

    if re.search(pattern_garage, informations['Kategorija']):
        type_of_real_estate = 'Garazno mesto'

    if re.search(pattern_parking, informations['Kategorija']):
        type_of_real_estate = 'Parking mesto'

    if re.search(pattern_build, informations['Kategorija']):
        type_of_real_estate = 'Gradjevinsko zemljiste'

    if re.search(pattertn_sports, informations['Kategorija']):
        type_of_real_estate = 'Sportski objekat'

    if re.search(pattern_lokal, informations['Kategorija']) or re.search(pattern_zgrada, informations['Kategorija']):
        type_of_real_estate = 'Komercijalni objekat'

    if re.search(pattern_work, informations['Kategorija']):
        type_of_real_estate = 'Poslovni prostor'

    offer = informations['Transakcija']
    location_of_real_estate = informations["Lokacija"]
    spm_string = map_processing('Kvadratura', informations)
    spm = string_to_int_processing(spm_string,'nepoznato')
    year_string = map_processing('Godina izgradnje',informations)
    year = string_to_int_processing(year_string, 'nepoznato')

    if type_of_real_estate == 'Kuca':
        area_string = map_processing('Površina zemljišta', informations)
        area = string_to_int_processing(area_string,'nepoznato')
    else:
        area = None
    if type_of_real_estate != 'Kuca':
        storey = map_processing('Spratnost', informations)
    else:
        storey = None
    num_of_floors_str = map_processing('Ukupan broj spratova', informations)
    num_of_floors = string_to_int_processing(num_of_floors_str, 'nepoznato')
    registration_string = map_processing("Uknjiženo", informations)
    if registration_string == 'Da':
        registration = True

    heating_type = map_processing('Grejanje', informations)
    num_of_rooms_str = map_processing('Ukupan broj soba', informations)
    num_of_rooms = string_to_int_processing(num_of_rooms_str, 'nepozanto')
    num_of_toilets_str = map_processing('Broj kupatila', informations)
    num_of_toilets = string_to_int_processing(num_of_toilets_str, 'nepoznato')

    real_estate = Real_estate.Real_Estate(external_id,type_of_real_estate, offer, location_of_real_estate, spm, year, area, storey, num_of_floors, registration, heating_type, num_of_rooms, num_of_toilets, parking, elevator, other)

    return real_estate

def extract_text_between_last_slashes(text):
    last_slash_index = text.rfind("/")

    if last_slash_index != -1:
        second_last_slash_index = text.rfind("/", 0, last_slash_index)

        if second_last_slash_index != -1:
            extracted_text = text[
                             second_last_slash_index + 1: last_slash_index]
            return extracted_text

    return None

def processing_all_real_estate(URL, limit):
    links, start_url = processing_home_page(URL)
    links_of_all_pages = find_links_recursive(start_url, int(limit))
    for page_link in links_of_all_pages:
        links.extend(finds_real_estate_links(page_link))
    real_estate_links = []
    for real_estate in links:
        real_estate_links.append(baseURL+"/"+real_estate)
    return real_estate_links
