import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from general_tools import pdump, progress_bar


path = "/Users/christianfinn/Desktop/chromedriver"
driver = webdriver.Chrome(path)
driver.set_page_load_timeout(6)

out_game_data = []


def get_scorers_from_link(url):
    try:
        driver.get(url)
    except TimeoutException:
        print('Unable to get scorers from %s' % url)
        return []
    time.sleep(3)
    scorer_list = driver.find_elements_by_class_name('c-generic-list')[0]
    scorer_elems = scorer_list.find_elements_by_class_name('c-event-item__header')
    scorers = [scorer_elem.get_attribute('innerHTML') for scorer_elem in scorer_elems]

    return scorers


def get_line_up_from_link(url):
    try:
        driver.get(url)
    except TimeoutException:
        print('Unable to get line ups from %s' % url)
        return []
    time.sleep(3)

    line_ups = {}
    hlf = []
    hll = []
    alf = []
    al_last = []
    hsf = []
    hsl = []
    asf = []
    asl = []
    hl_names = []
    hl_counter = 0
    al_names = []
    al_counter = 0
    hs_names = []
    hs_counter = 0
    as_names = []
    as_counter = 0

    home_lus_lst = driver.find_elements_by_class_name('c-line-up__starting-eleven-wrapper')[0]
    away_lus_lst = driver.find_elements_by_class_name('c-line-up__starting-eleven-wrapper')[1]
    home_subs_lst = driver.find_elements_by_class_name('c-line-up__substitutes-wrapper')[0]
    away_subs_lst = driver.find_elements_by_class_name('c-line-up__substitutes-wrapper')[1]

    home_lus_f = home_lus_lst.find_elements_by_class_name('c-player-panel__first-name')
    home_lus_l = home_lus_lst.find_elements_by_class_name('c-player-panel__last-name')
    away_lus_f = away_lus_lst.find_elements_by_class_name('c-player-panel__first-name')
    away_lus_l = away_lus_lst.find_elements_by_class_name('c-player-panel__last-name')
    home_subs_f = home_subs_lst.find_elements_by_class_name('c-player-panel__first-name')
    home_subs_l = home_subs_lst.find_elements_by_class_name('c-player-panel__last-name')
    away_subs_f = away_subs_lst.find_elements_by_class_name('c-player-panel__first-name')
    away_subs_l = away_subs_lst.find_elements_by_class_name('c-player-panel__last-name')

    hlf += [home_lu_f.get_attribute('innerHTML') for home_lu_f in home_lus_f]
    hll += [home_lu_l.get_attribute('innerHTML') for home_lu_l in home_lus_l]
    for y in hlf:
        hl_names.append(y.replace('&nbsp;', ' ') + hll[hl_counter])
        hl_counter += 1
    line_ups['home_line_up'] = hl_names

    alf += [away_lu_f.get_attribute('innerHTML') for away_lu_f in away_lus_f]
    al_last += [away_lu_l.get_attribute('innerHTML') for away_lu_l in away_lus_l]
    for y in alf:
        al_names.append(y.replace('&nbsp;', ' ') + al_last[al_counter])
        al_counter += 1
    line_ups['away_line_up'] = al_names

    hsf += [home_sub_f.get_attribute('innerHTML') for home_sub_f in home_subs_f]
    hsl += [home_sub_l.get_attribute('innerHTML') for home_sub_l in home_subs_l]
    for y in hsf:
        hs_names.append(y.replace('&nbsp;', ' ') + hsl[hs_counter])
        hs_counter += 1
    line_ups['home_subs'] = hs_names

    asf += [away_sub_f.get_attribute('innerHTML') for away_sub_f in away_subs_f]
    asl += [away_sub_l.get_attribute('innerHTML') for away_sub_l in away_subs_l]
    for y in asf:
        as_names.append(y.replace('&nbsp;', ' ') + asl[as_counter])
        as_counter += 1
    line_ups['away_subs'] = as_names

    return line_ups


def scrape_data_teams(match_data):
    out_dict = {}
    teams = (match_data.findAll('div', {'class': 'c-team-item'}))
    for j in range(len(teams)):
        team_out = teams[j].findAll('span', {'class': 'c-team-item__name'})
        team_scores = teams[j].findAll('div', {'class': 'c-team-item__score'})
        if j == 0:
            out_dict['home_team'] = team_out[0].get_text()
            out_dict['home_score'] = team_scores[0].get_text().replace((str('\xa0')), '')
        elif j == 1:
            out_dict['away_team'] = team_out[0].get_text()
            out_dict['away_score'] = team_scores[0].get_text().replace((str('\xa0')), '')
        else:
            print('error')

    game_link = match_data.findAll('a', {'class': 'c-link'})[0]
    game_url = 'https://www.nwslsoccer.com' + game_link['href']
    out_dict['date'] = game_url[-10:]

    out_dict['scorers'] = get_scorers_from_link(game_url + '#boxscore')
    out_dict['line_up'] = get_line_up_from_link(game_url + '#line-up')

    return out_dict


base_url = "https://www.nwslsoccer.com"
seasons = ['2016', '2017', '2018', '2019', '2020%20Challenge%20Cup', '2020%20Fall%20Series']

for season in seasons:
    print(progress_bar(seasons.index(season), len(seasons)))
    test_url = base_url + "/schedule?season=" + season
    result = requests.get(test_url)
    soup = BeautifulSoup(result.content, 'lxml')
    matches = soup.findAll('div', {'class': 'c-match-item'})

    n_games = len(matches)
    for i in range(n_games):
        progress_bar(i, n_games)
        out_game_data.append(scrape_data_teams(matches[i]))

pdump(out_game_data, 'NWSL_game_data(2).pkl')
driver.quit()
