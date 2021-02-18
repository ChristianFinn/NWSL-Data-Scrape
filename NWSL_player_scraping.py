import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from general_tools import pdump, progress_bar


path = "/Users/christianfinn/Desktop/chromedriver"
driver = webdriver.Chrome(path)
driver.set_page_load_timeout(10)

out_player_data = []


def get_player_detail(url):
    try:
        driver.get(url)
    except TimeoutException:
        print('Unable to get player detail from %s' % url)
        return []
    time.sleep(5)
    driver.switch_to.frame(0)

    stats = driver.find_elements_by_class_name('Opta-Stats')

    out = {}

    for stat in stats:
        soup_det = BeautifulSoup(stat.get_attribute('innerHTML'), 'lxml')
        labels = soup_det.select('.Opta-Graph-Title')
        values = soup_det.select('.Opta-Value')
        if len(labels) != len(values):
            labels = soup_det.select('.Opta-Label')

        for k in range(len(labels)):
            label = labels[k].get_text()
            value = values[k].get_text()
            out[label] = value
    return out


def get_data_from_link(player_link_url):
    seasons_played = []
    out_detail = {}
    pl_result = requests.get(player_link_url)
    pl_soup = BeautifulSoup(pl_result.content, 'lxml')
    buttons = pl_soup.select('option')
    for button in buttons:
        pl_season = button.get_text()
        if pl_season not in seasons_played:
            seasons_played.append(pl_season)

    for j in range(len(seasons_played)):
        seasons_played[j] = seasons_played[j].replace(' ', '%20')

    for season in seasons_played:
        season_url = player_link_url + '?statsSeason=' + season

        out_detail[season] = get_player_detail(season_url)

    return out_detail


def scrape_data_players(player):
    out_dict = {}
    names = player.select('.c-players-table-row__player-name')[0].find_all('span')
    out_dict['first_name'] = names[0].get_text()
    out_dict['last_name'] = names[1].get_text()

    out_dict['number'] = player.select('.number')[0].get_text()

    out_dict['position'] = player.select('.position')[0].get_text()

    out_dict['nationality'] = player.select('.nationality')[0].get_text()

    out_dict['dob'] = player.select('.dob')[0].get_text()

    out_dict['height'] = player.select('.height')[0].get_text()

    out_dict['team'] = player.select('.team')[0].get_text()

    player_link = player.findAll('a', {'class': 'c-link'})[0]

    out_dict['detail'] = get_data_from_link('https://www.nwslsoccer.com' + player_link['href'])
    print(out_dict)
    return out_dict


players_url = 'https://www.nwslsoccer.com/players'

result = requests.get(players_url)
soup = BeautifulSoup(result.content, 'lxml')
player_scrape = soup.select('.c-players-table-row')
print(player_scrape)

n_players = len(player_scrape)
for i in range(n_players):
    progress_bar(i, n_players)
    # out_player_data.append(scrape_data_players(player_scrape[i]))

pdump(out_player_data, 'NWSL_player_data.pkl(2)')
driver.quit()
