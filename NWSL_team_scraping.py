import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from general_tools import pdump, progress_bar


path = "/Users/christianfinn/Desktop/chromedriver"
driver = webdriver.Chrome(path)
driver.set_page_load_timeout(10)

out_team_data = []
team_names = ['/teams/western-new-york-flash', '/teams/boston-breakers']


def get_team_detail(url):
    try:
        driver.get(url)
    except TimeoutException:
        print('Unable to get team detail from %s' % url)
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


def get_data_from_link(team_link_url):
    try:
        driver.get(team_link_url)
        time.sleep(2)
    except TimeoutException:
        print('Unable to get team detail from %s' % team_link_url)
        return []
    time.sleep(2)
    seasons_played = []
    out_detail = {}
    pl_result = requests.get(team_link_url)
    time.sleep(2)
    pl_soup = BeautifulSoup(pl_result.content, 'lxml')
    buttons = pl_soup.select('option')
    time.sleep(2)
    for button in buttons:
        pl_season = button.get_text()
        if pl_season not in seasons_played:
            seasons_played.append(pl_season)

    for j in range(len(seasons_played)):
        seasons_played[j] = seasons_played[j].replace(' ', '%20')

    for season_lnk in seasons_played[3:]:
        season_url = team_link_url + '?statsSeason=' + season_lnk
        out_detail[season_lnk] = get_team_detail(season_url)

    return out_detail


def scrape_data_team(team_in):
    out_dict = {}
    team_in = team_in.find(href=True)
    team_link = team_in['href']
    print(team_link)
    team_name = team_in.find_all('span')[2]
    team_name = team_name.get_text()
    print(team_name)
    out_dict[team_name] = get_data_from_link('https://www.nwslsoccer.com' + team_link)
    return out_dict


base_url = "https://www.nwslsoccer.com"
seasons = ['2016', '2017', '2018', '2019', '2020%20Challenge%20Cup', '2020%20Fall%20Series', '2021']

for season in seasons:
    print(progress_bar(seasons.index(season), len(seasons)))
    test_url = base_url + "/standings?season=" + season
    result = requests.get(test_url)
    soup = BeautifulSoup(result.content, 'lxml')
    teams = soup.findAll('div', {'class': 'c-table-row'})

    n_teams = len(teams)
    for i in range(n_teams):
        progress_bar(i, n_teams)
        team = teams[i].find(href=True)
        team_href = team['href']

        if team_href not in team_names:
            team_names.append(team_href)
            out_team_data.append(scrape_data_team(teams[i]))
            print(out_team_data)

pdump(out_team_data, 'NWSL_team_data(2).pkl')
driver.quit()
