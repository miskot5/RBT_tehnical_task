import requests
from bs4 import BeautifulSoup
import re
import Real_estate
import Location

pattern_elevator = r"(?i)\bLift\b"
pattern_kuca = r"\b(K|k)uća\b"
pattern_stan = r"\b(S|s)tan\b"
pattern_zgrada = r"(Z|z)grada"
pattern_garage = r"(G|g)araž"
pattern_parking = r"(P|p)ark"
pattern_build = r"(G|g)radjevin"
pattern_gars = r"(G|g)arsonjera"
pattertn_sports = r"(S|s)port"
pattern_lokal = r"(L|l)okal"
pattern_other = re.compile(r'\b(?:(T|t)erasa|(L|l)odja|(B|b)alkon)\b', re.IGNORECASE)

def processing_home_page(URL):
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    premium_offers = soup.select('.premium-offers-item')

    links = []
    for offer in premium_offers:
        href = offer.find('a', href = True)
        item_link = URL + href['href'][1:]
        links.append(item_link)

    return links

#ako nismo u html reprezentaciji nasli odredjeni podatak, svakako zelimo da imamo podatak o tome u mapi, da bismo u bazi mogli to da cuvamo kao null
def map_processing(key, map):
    if key not in map:
        map[key] = 'nepoznato'
    if map[key].isdigit():
        return int(map[key])
    else:
        return map[key]

#kod integer atributa, vrednost -1 oznacavace nepostojanje vrednosti
def string_to_int_processing(attribute_string, string):
    if attribute_string == string:
        return -1
    else:
        result = re.sub(r'\D', '', str(attribute_string))
        if result == '':
            return -1
        else:
            return int(result)

def location_processing(name,city,map):
    try:
        map[name] = city
    except KeyError:
        map[name] = 'nepoznato'

def real_estate_processing(link):
    resp = requests.get(link)
    soup = BeautifulSoup(resp.text, 'html.parser')
    infos_soup = soup.select('.property__amenities > ul > li')


    informations = {}
    for info in infos_soup:
        information = re.sub('\s{2,}','',info.text)
        separator = ':'

        if separator in information:
            separator_position = information.index(separator)
            informations[information[:separator_position]] = information[separator_position + 1:]
        if separator not in information:
            if re.search(pattern_elevator, information) is not None:
                informations["Lift"] = "Da"
            if re.search(pattern_other, information) is not None:
                informations["Ostalo"] = "Da"

    location_soup = soup.select(".stickyBox__Location")
    for loc in location_soup:
        try:
            city =re.sub(r'\s+', ' ', loc.text.split(",")[0])
            part_of_city = re.sub(r'\s+', ' ', loc.text.split(",")[1])
        except IndexError:
            part_of_city = "nepoznato"

    informations["Lokacija"] =  re.sub(r",\s+", ",", city +"," + part_of_city)

    type_of_real_estate = 'Nepoznato'
    if re.search(pattern_kuca, informations['Kategorija']):
        type_of_real_estate = 'Kuca'
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
    offer = informations['Transakcija']
    location_of_real_estate = informations["Lokacija"]
    spm_string = map_processing('Kvadratura', informations)
    spm = string_to_int_processing(spm_string,'nepoznato')
    year_string = map_processing('Godina izgradnje',informations)
    year = string_to_int_processing(year_string, 'nepoznato')
    area = 0
    storey = map_processing('Spratnost', informations)
    num_of_floors_str = map_processing('Ukupan broj spratova', informations)
    num_of_floors = string_to_int_processing(num_of_floors_str, 'nepoznato')
    registration = map_processing('Uknjiženo', informations)
    heating_type = map_processing('Grejanje', informations)
    num_of_rooms_str = map_processing('Ukupan broj soba', informations)
    num_of_rooms = string_to_int_processing(num_of_rooms_str, 'nepozanto')
    num_of_toilets_str = map_processing('Broj kupatila', informations)
    num_of_toilets = string_to_int_processing(num_of_toilets_str, 'nepoznato')
    parking = map_processing('Parking', informations)
    elevator = map_processing('Lift', informations)
    other = map_processing('Ostalo', informations)

    real_estate = Real_estate.Real_Estate(type_of_real_estate, offer, location_of_real_estate, spm, year, area, storey, num_of_floors, registration, heating_type, num_of_rooms, num_of_toilets, parking, elevator, other)

    return real_estate








