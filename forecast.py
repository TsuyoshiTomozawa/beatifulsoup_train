import requests
from urllib.parse import urlparse, quote_plus, unquote
from bs4 import BeautifulSoup

def url_to_soup(url):
    req = requests.get(url)
    return BeautifulSoup(req.content, 'html.parser')

def get_father(url):
    soup = url_to_soup(url)
    blood_list  = soup.find_all(class_='blood_table')[0].find_all("a")
    
    father = blood_list[0]
    return father

def get_horse_list(url):
    return [x.get('title') for x in soup.select("td.horsename > div > a")]

def get_link_list(url):
    return [x.get('href') for x in soup.select("td.horsename > div > a")]

def get_horse_data(soup):
    datas = []
    for horse in soup.select("td.horsename > div > a"):
        horsename = horse.get("title")
        link = horse.get("href")
        datas.append({"horsename":horsename, "link":link})

    return datas
def get_archievement(url):
    soup = url_to_soup(url)
    
    archievements = soup.find(class_="db_h_race_results").find('tbody').find_all('tr')
    #print(archievements)
    #exit()
    archievement = archievements[0].find_all("td")
    corner_position = archievement[20].string
    datas = {}
    datas['pre_race'] = archievement[14].string
    datas['corner_position'] = corner_position
    datas['popular'] = archievement[10].string
    datas['rank'] = archievement[11].string
    
    archievements.pop(0)
    
    preceding_flag = False
    for result in archievements:
        archievement = result.find_all("td")
        #先行
        corner_position  = archievement[20].string.split('-')[0]
        rank = archievement[11].string

        if rank.isnumeric() == False or corner_position.isnumeric() == False:
            continue;
        if int(corner_position) < 5 and int(rank) <= 3:
            preceding_flag = True
            break

    datas['preceding_flag'] = preceding_flag

    return datas


def get_race_data(soup):
    return soup.find(class_="mainrace_data")

def get_fathers_list():
    # 馬ゲノム
    url = "http://www.keiba-m.com/genomedic/keitai_ban.html"
    soup = url_to_soup(url)
    father_list = soup.find_all(class_="p3")
    datas = {}
    for father in father_list:
        fathername = father.find("a").string
        link = father.find("a").get("href")
        datas[fathername] = {"name":fathername, "link":link}
        #datas.append({"name":fathername, "link":link})

    return datas


url = "https://race.netkeiba.com/?pid=race_old&id=c201905030511&mode=top"
soup = url_to_soup(url)

# 父　血統データ取得
fathers_list = get_fathers_list()

# レース情報取得
race_data = get_race_data(soup)
race = race_data.find(class_="racedata").find('p').string
race_type = race[0]
range = race[1:5]

result = {}
datas = get_horse_data(soup)
for data in datas:
    link = data['link']
    
    # 最新レース戦績
    archievement_last = get_archievement(link)
    pre_range = archievement_last['pre_race'][1:5]
    corner_pos = archievement_last['corner_position']
    rank = archievement_last['rank']
    popular = archievement_last['popular']

    if rank.isnumeric() == False or popular.isnumeric() == False:
        continue;

    #差して凡走
    general_run_flg = False
    if int(corner_pos.split('-')[-2]) >= 5 and int(rank) > 3:
        general_run_flg = True

    if pre_range < range:
        range_comparison = "延長"
    elif pre_range > range:
        range_comparison = "短縮"
    elif pre_range == range:
        range_comparison = "同距離"

    result[data['horsename']] = {"range_comparison":range_comparison, 'corner_position': corner_pos.split('-')[-2], "general_run_flg":general_run_flg}

    '''
    father = get_father(link).get('title')
    print(father)
    if(father in fathers_list):
        print("found horse!", father)
        # 今回の複勝率を取得
        link = fathers_list[father]['link']
        link = "http://www.keiba-m.com/genomedic/genome2018.files/" + quote_plus(father+".htm", encoding='utf-8')

        soup = url_to_soup(link)
        print(soup)
        name = soup.find_next(string=race_type+range)
        name = soup.find_all(string="芝1200")
        print(name)
        exit()
    '''
    
#print(result)
#exit()
for horsename, value in result.items():
    if value['range_comparison'] == "短縮" and int(value['corner_position']) >= 5 and value['general_run_flg']:
        print(horsename)




