from bs4 import BeautifulSoup as bs
import re
from contextlib import suppress
import traceback
from dateutil import parser
import requests
import xlsxwriter
from difflib import SequenceMatcher
from datetime import datetime, date
from datetime import timedelta
from webauto_base import webauto_base
import time
import math
import logging
import os
import json
espnArray =  []
collageArray = []
spreadArray = []
jsonArray = None
def get_espn():
    try:        
        print("Request to https://www.espn.com/mens-college-basketball/standings...")
        url = "https://www.espn.com/mens-college-basketball/standings"
        #Get the Page Content String from the Espn      
        pageString = requests.get(url).text
        soup = bs(pageString, 'html.parser')

        sections = soup.findAll('section', {'class':'ResponsiveTable'})

        for section in sections:
            conference_name = list(section.children)[0].get_text()

            tr = section.findChildren("tr", {'class','Table__TR--sm'})

            for i in range(int(len(tr)/2)):                
                team_name = tr[i].find("abbr")
                point = tr[int(len(tr)/2)+i].findChildren("span", {'class', 'stat-cell'})
                if team_name is not None:
                    espnArray.append({
                        "conference_name" : conference_name,
                        "team_name" : team_name['title'],
                        "abbr" : team_name.get_text(),
                        "c_w_l": point[0].get_text(),
                        "c_gb": point[1].get_text(),
                        "c_pct": point[2].get_text(),
                        "o_w_l": point[3].get_text(),
                        "o_pct": point[4].get_text(),
                        "o_home": point[5].get_text(),
                        "o_away": point[6].get_text(),
                        "o_strk": point[7].get_text(),
                    })        
    except Exception as e:
        print(str(e))
        logging.info(str(e))
        traceback.print_exc()

def get_colleage():
    try:        
        print("Request to https://www.espn.com/mens-college-basketball/bpi/_/view/overview/sort/sospastrank/dir/asc...")
        url = "https://www.espn.com/mens-college-basketball/bpi/_/view/overview/sort/sospastrank/dir/asc"
        pg = 1
        while pg < 100:
            try:
                url = "https://www.espn.com/mens-college-basketball/bpi/_/view/overview/sort/sospastrank/page/" + str(pg) + "/dir/asc"
                page = requests.get(url).text
                soup = bs(page, 'html.parser')

                no_data = soup.find('div', {'class' : 'no-data-available'})
                if no_data is not None and no_data.get_text() == "No data available.":
                    break
                
                trs = soup.findAll('tr')

                for tr in trs:
                    try:
                        td = tr.findChildren('td')
                        if len(td) == 8:
                            collageArray.append({
                                'team_name' : td[1].find('span',{'class','team-names'}).get_text(),
                                'abbr' : td[1].find('abbr').get_text(),
                                'conf' : '',
                                'bpi_rk' : td[4].get_text(),
                                'sos_rk' : td[5].get_text(),
                                'sor_rk' : td[6].get_text(),
                            })
                    except:
                        pass                   

            except Exception as exx:
                print(str(exx))
                logging.info(str(exx))
                pass
            pg = pg + 1

    except Exception as e:
        print(str(e))
        logging.info(str(e))
        traceback.print_exc()

class get_spread(webauto_base):
    def __del__(self):
        super().__init__()

    def automate(self, day):
        try:            
            url = "https://www.sportsbookreview.com/betting-odds/ncaa-basketball/?date=" + day
            pageString = requests.get(url).text
            pattern = re.compile("window.__INITIAL_STATE__=(.*?)}};")
            data = pattern.findall(pageString)
            result = json.loads(data[0] + '}}')
            #print(len(result['events']['events']))
                        
            print("Automation to get spreads...")
            print(url)

            self.start_browser(False)
            self.navigate(url)

            self.delay_me(3)

            xpath = "//div[@id='bettingOddsGridContainer']/div[3]/*"
            bettingContainer = self.browser.find_elements_by_xpath(xpath)
                      
            # #print(day)
            xpath = "//div[@id='bettingOddsGridContainer']//div//div//div//div[@data-vertical-sbid='time']/div//span"
            p_time = self.browser.find_elements_by_xpath(xpath)            

            xpath = "//div[@id='bettingOddsGridContainer']//div//div//div//section//a//span"
            teams = self.browser.find_elements_by_xpath(xpath)

            #print(len(teams))
            xpath = "//div[@id='bettingOddsGridContainer']//div//div//div//section[@data-vertical-sbid='-1']//span[@data-cy='odd-grid-opener-league']"
            opener = self.browser.find_elements_by_xpath(xpath)

            bookmarker = None
            five_times = None
            bovada = None

            count = 0
            while True:
                xpath = "//div[@id='bettingOddsGridContainer']//div//div//div//section[@data-vertical-sbid='93']//span[@data-cy='odd-grid-league']"
                bookmarker = self.browser.find_elements_by_xpath(xpath)
                                
                xpath = "//div[@id='bettingOddsGridContainer']//div//div//div//section[@data-vertical-sbid='19']//span[@data-cy='odd-grid-league']"
                five_times = self.browser.find_elements_by_xpath(xpath)

                xpath = "//div[@id='bettingOddsGridContainer']//div//div//div//section[@data-vertical-sbid='1618']//span[@data-cy='odd-grid-league']"
                bovada = self.browser.find_elements_by_xpath(xpath)
                                
                if len(opener) == len(bookmarker) or len(opener) == len(five_times) or len(opener) == len(bovada):
                    break

                count = count + 1
                if count > 100 and (len(bookmarker) == 0 or len(five_times) == 0 or len(bovada) == 0):
                    break                               
                
            if len(bookmarker) == 0 or len(five_times) == 0 or len(bovada) == 0:
                xpath = "//i[@class='sbr-icon-chevron-right']"
                right = self.browser.find_element_by_xpath(xpath)
                right = right.find_element_by_xpath("..")
                right.click()

                self.delay_me(3)

                if len(bookmarker) == 0:
                    xpath = "//div[@id='bettingOddsGridContainer']//div//div//div//section[@data-vertical-sbid='93']//span[@data-cy='odd-grid-league']"
                    bookmarker = self.browser.find_elements_by_xpath(xpath)
                                
                if len(five_times) == 0:
                    xpath = "//div[@id='bettingOddsGridContainer']//div//div//div//section[@data-vertical-sbid='19']//span[@data-cy='odd-grid-league']"
                    five_times = self.browser.find_elements_by_xpath(xpath)

                if len(bovada) == 0:
                    xpath = "//div[@id='bettingOddsGridContainer']//div//div//div//section[@data-vertical-sbid='1618']//span[@data-cy='odd-grid-league']"
                    bovada = self.browser.find_elements_by_xpath(xpath)

                right.click()

                self.delay_me(3)

                if len(bookmarker) == 0:
                    xpath = "//div[@id='bettingOddsGridContainer']//div//div//div//section[@data-vertical-sbid='93']//span[@data-cy='odd-grid-league']" #93
                    bookmarker = self.browser.find_elements_by_xpath(xpath)
                                
                if len(five_times) == 0:
                    xpath = "//div[@id='bettingOddsGridContainer']//div//div//div//section[@data-vertical-sbid='19']//span[@data-cy='odd-grid-league']"
                    five_times = self.browser.find_elements_by_xpath(xpath)

                if len(bovada) == 0:
                    xpath = "//div[@id='bettingOddsGridContainer']//div//div//div//section[@data-vertical-sbid='1618']//span[@data-cy='odd-grid-league']"
                    bovada = self.browser.find_elements_by_xpath(xpath) 

            print("Processing...")
            bettingDate = None
            i = 0
            for divs in bettingContainer:
                try:
                    bettingDate = divs.find_element_by_xpath("./div/div/span")
                    if bettingDate.text != "Box Scores":
                        bettingDate = bettingDate.text
                        continue

                    if bettingDate.text == "Box Scores":
                        continue
                                        
                except:
                    pass

                #result['events']['events']
                #                                 
                try:
                    time = ''
                    length = len(divs.find_elements_by_xpath("./div"))
                    if length >= 2 and bettingDate is not None:                        
                        data_eid = None
                        first_t = None
                        second_t = None

                        try:
                            data_eid = divs.find_element_by_xpath("./div[1]").get_attribute('data-horizontal-eid')
                        
                            if data_eid is not None:
                                for tmt in result['events']['events'][data_eid]["participants"]:
                        
                                    if result['events']['events'][data_eid]["participants"][tmt]['ih'] == False:
                                        first_t = result['events']['events'][data_eid]["participants"][tmt]['source']['abbr']
                                    else:
                                        second_t = result['events']['events'][data_eid]["participants"][tmt]['source']['abbr']                 
                        except:
                            pass
                        
                        
                        try:
                            time = divs.find_element_by_xpath("./div[1]//div[1]//div[2]//span").text
                            date_time_obj = datetime.strptime(time.replace(' ',''), '%I:%M%p')
                            time = date_time_obj.strftime("%H:%M")
                        except:
                            pass
                                
                        point_A_T = ""
                        point_B_T = ""                        
                        diff_A = 0
                        diff_B = 0
                        if length == 3:
                            points = divs.find_elements_by_xpath("./div[2]/div/div")
                            try:                                
                                point_A_T = int(points[len(points)-1].text.split("\n")[0])
                                point_B_T = int(points[len(points)-1].text.split("\n")[1])
                                diff_A = point_A_T - point_B_T
                                diff_B = point_B_T - point_A_T
                            except:
                                pass                            

                        opener_f = "-"
                        opener_s = "-"
                        try:
                            opener_val = opener[i].find_elements_by_xpath("./span")
                            opener_f = opener_val[0].text
                            opener_s = opener_val[1].text
                        except:
                            pass

                        bookmarker_f = "-"
                        bookmarker_s = "-"
                        try:
                            bookmarker_val = bookmarker[i].find_elements_by_xpath("./span")
                            bookmarker_f = bookmarker_val[0].text
                            bookmarker_s = bookmarker_val[1].text
                        except:
                            pass
                        

                        five_times_f = "-"
                        five_times_s = "-"
                        try:
                            five_times_val = five_times[i].find_elements_by_xpath("./span")
                            five_times_f = five_times_val[0].text
                            five_times_s = five_times_val[1].text
                        except:
                            pass

                        bovada_f = "-"
                        bovada_s = "-"
                        try:
                            bovada_val = bovada[i].find_elements_by_xpath("./span")
                            bovada_f = bovada_val[0].text
                            bovada_s = bovada_val[1].text
                        except:
                            pass

                        spreadArray.append({
                            'time' : time,
                            'team' : teams[i].text,
                            'abbr': first_t,
                            'opener' : getOdds(opener_f),
                            'opener_odds': getOdds(opener_s),
                            'bookmarker' : getOdds(bookmarker_f),
                            'bookmarker_odds' : getOdds(bookmarker_s),
                            'five_times' : getOdds(five_times_f),
                            'five_times_odds' : getOdds(five_times_s),
                            'bovada' : getOdds(bovada_f),
                            'bovada_odds' : getOdds(bovada_s),                            
                            'date': bettingDate,
                            'point': point_A_T,
                            'diff': diff_A,
                            'update_day': day,
                        })
                        
                        opener_f = "-"
                        opener_s = "-"
                        try:
                            opener_val = opener[i+1].find_elements_by_xpath("./span")
                            opener_f = opener_val[0].text
                            opener_s = opener_val[1].text
                        except:
                            pass

                        bookmarker_f = "-"
                        bookmarker_s = "-"
                        try:
                            bookmarker_val = bookmarker[i+1].find_elements_by_xpath("./span")
                            bookmarker_f = bookmarker_val[0].text
                            bookmarker_s = bookmarker_val[1].text
                        except:
                            pass
                        
                        five_times_f = "-"
                        five_times_s = "-"
                        try:
                            five_times_val = five_times[i+1].find_elements_by_xpath("./span")
                            five_times_f = five_times_val[0].text
                            five_times_s = five_times_val[1].text
                        except:
                            pass

                        bovada_f = "-"
                        bovada_s = "-"
                        try:
                            bovada_val = bovada[i+1].find_elements_by_xpath("./span")
                            bovada_f = bovada_val[0].text
                            bovada_s = bovada_val[1].text
                        except:
                            pass

                        spreadArray.append({
                            'time' : time,
                            'team' : teams[i+1].text,
                            'abbr': second_t,
                            'opener' : getOdds(opener_f),
                            'opener_odds': getOdds(opener_s),
                            'bookmarker' : getOdds(bookmarker_f),
                            'bookmarker_odds' : getOdds(bookmarker_s),
                            'five_times' : getOdds(five_times_f),
                            'five_times_odds' : getOdds(five_times_s),
                            'bovada' : getOdds(bovada_f),
                            'bovada_odds' : getOdds(bovada_s),
                            'date': bettingDate,
                            'point': point_B_T,
                            'diff': diff_B,
                            'update_day': day,
                        })
                        i = i + 2
                except:
                    pass
           
            self.quit_browser()
        except Exception as e:
            print(str(e))
            logging.info(str(e))
            traceback.print_exc()

def findDay():
    return date.today().weekday()

def getToday():
    return datetime.today().strftime("%Y-%m-%d")

def get_conf(team_name):

    try:
        tmp = espnArray[0]
        pt = 0
        for espn in espnArray:
            if espn['abbr'].lower() == team_name.lower():
                return espn
                break
            #if pt < SequenceMatcher(None, espn['abbr'].lower(), team_name.lower()).ratio():
                #pt = SequenceMatcher(None, espn['abbr'].lower(), team_name.lower()).ratio()
                #tmp = espn

        return None
    except:
        logging.info("Not found the get_conf of team_name")
        return None

def get_conf1(team_name):

    try:
        tmp = espnArray[0]
        pt = 0
        for espn in espnArray:           
            if pt < SequenceMatcher(None, espn['team_name'].lower(), team_name.lower()).ratio():
                pt = SequenceMatcher(None, espn['team_name'].lower(), team_name.lower()).ratio()
                tmp = espn

        return tmp
    except:
        logging.info("Not found the get_conf of team_name")
        return None

def get_coll(team_name):
    try:
        tmp = collageArray[0]
        pt = 0
        for collage in collageArray:
            if collage['abbr'].lower() == team_name.lower():
                return collage
                break

        return None
    except:
        logging.info("Not found the coll of team_name")
        return None

def get_coll1(team_name):
    try:
        tmp = collageArray[0]
        pt = 0
        for collage in collageArray:
            
            if pt < SequenceMatcher(None, collage['team_name'].lower(), team_name.lower()).ratio():
                pt = SequenceMatcher(None, collage['team_name'].lower(), team_name.lower()).ratio()
                tmp = collage

        return tmp
    except:
        logging.info("Not found the coll of team_name")
        return None

def getCurrentDate():
    return datetime.today().day    

def getCurrentMonth():
    return datetime.today().strftime("%b")

def getOdds(odds):
    try:
        odds = odds.replace('½','.5')
        if odds == 'PK':
            odds = '0'
        elif odds == '-':
            odds = '0'

        return odds

    except:
        return '0' 

def make_spread():
    print("Making...")
    try:
        today = datetime.now()
        allData = []
        dayNumber = findDay()
        filename = "result_" + today.strftime("%Y%m%d%H%M%S") + ".xlsx"
            
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet('NCAA Teams')
        
        bold = workbook.add_format({'bold': True})
        worksheet.write(0, 0, "Team", bold)
        worksheet.write(0, 1, "Conference", bold)
        worksheet.write(0, 2, "W-L (Conference)", bold)
        worksheet.write(0, 3, "GB", bold)
        worksheet.write(0, 4, "PCT", bold)
        worksheet.write(0, 5, "W-L (Overall)", bold)
        worksheet.write(0, 6, "PCT", bold)
        worksheet.write(0, 7, "Home", bold)
        worksheet.write(0, 8, "PCT", bold)
        worksheet.write(0, 9, "Away", bold)
        worksheet.write(0, 10, "PCT", bold)
        worksheet.write(0, 11, "STRK", bold)
                            
        index = 1
        for espn in espnArray:
            worksheet.write(index, 0, espn['team_name'])
            worksheet.write(index, 1, espn['conference_name'])
            worksheet.write(index, 2, espn['c_w_l'])
            worksheet.write(index, 3, espn['c_gb'])
            worksheet.write(index, 4, espn['c_pct'])
            worksheet.write(index, 5, espn['o_w_l'])
            worksheet.write(index, 6, espn['o_pct'])
            worksheet.write(index, 7, espn['o_home'])
            worksheet.write(index, 9, espn['o_away'])
            worksheet.write(index, 11, espn['o_strk'])

            result = 0
            try:
                array = espn["o_home"].split('-')                   
                result = round(int(array[0])/(int(array[0])+int(array[1])) * 100)
            except:
                result = 0
                pass
            worksheet.write(index, 8, str(result) + "%")

            result = 0
            try:
                array = espn["o_away"].split('-')                   
                result = round(int(array[0])/(int(array[0])+int(array[1])) * 100)
            except:
                result = 0
                pass
            worksheet.write(index, 10, str(result) + "%")

            index = index + 1
                
        
        weekday = findDay()

        bold = workbook.add_format({'bold': True})
        green_format1 = workbook.add_format()
        green_format1.set_pattern(1)  # This is optional when using a solid fill.
        green_format1.set_bg_color('green')

        tomato_format2 = workbook.add_format()
        tomato_format2.set_pattern(1)  # This is optional when using a solid fill.
        tomato_format2.set_bg_color('#ff6347')

        magenta_format = workbook.add_format()
        magenta_format.set_pattern(1)  # This is optional when using a solid fill.
        magenta_format.set_bg_color('magenta')

        for i in range(weekday+1):                
            findex = weekday -i
            format_day = datetime.strftime(datetime.now() - timedelta(findex), '%m/%d/%Y')   
            day = datetime.strftime(datetime.now() - timedelta(findex), '%Y%m%d')   
            date = datetime.strftime(datetime.now() - timedelta(findex), '%d')
            month = datetime.strftime(datetime.now() - timedelta(findex), '%b')

            worksheet = workbook.add_worksheet(month + '.' + date)

            # worksheet.write(0, 0, "Date (MM/DD/YY) ", bold)
            # worksheet.write(0, 1, "Time", bold)
            # worksheet.write(0, 2, "Team", bold)
            # worksheet.write(0, 3, "Conf", bold)
            # worksheet.write(0, 4, "Spread (Opener)", bold)
            # worksheet.write(0, 5, "Odds", bold)
            # worksheet.write(0, 6, "Spread (BookMaker)", bold)
            # worksheet.write(0, 7, "Odds", bold)
            # worksheet.write(0, 8, "Spread (5 Dimes)", bold)
            # worksheet.write(0, 9, "Odds", bold)
            # worksheet.write(0, 10, "Spread (Bovada)", bold)
            # worksheet.write(0, 11, "Odds", bold)
            # worksheet.write(0, 12, "Away/Home Overall Record", bold)
            # worksheet.write(0, 13, "Percentage", bold)
            # worksheet.write(0, 14, "W-L (Overall) PCT", bold)
            # worksheet.write(0, 15, "STRK", bold)
            # worksheet.write(0, 16, "BPI Rank", bold)
            # worksheet.write(0, 17, "SOS Rank", bold)
            # worksheet.write(0, 18, "SOR Rank", bold)
            # worksheet.write(0, 19, "Score", bold)
            # worksheet.write(0, 20, "P.D", bold)
            # worksheet.write(0, 21, "Away 30% below", bold)
            # worksheet.write(0, 22, "Home 70% above", bold)
            # worksheet.write(0, 23, "Sharp-Square", bold)
            # worksheet.write(0, 24, "Wager", bold)
            # worksheet.write(0, 25, "Total", bold)
            # worksheet.write(0, 26, "Home Cover", bold)
            worksheet.write(0, 0, "Date", bold)
            worksheet.write(0, 1, "Time", bold)
            worksheet.write(0, 2, "Team", bold)
            worksheet.write(0, 3, "Conf", bold)
            worksheet.write(0, 4, "Opener", bold)
            worksheet.write(0, 5, "Bookmaker", bold)
            worksheet.write(0, 6, "5 Dimes", bold)
            worksheet.write(0, 7, "Bovada", bold)
            worksheet.write(0, 8, "Away/Home", bold)
            worksheet.write(0, 9, "%", bold)
            worksheet.write(0, 10, "Overall %", bold)
            worksheet.write(0, 11, "STRK", bold)
            worksheet.write(0, 12, "BPI Rank", bold)
            worksheet.write(0, 13, "SOS Rank", bold)
            worksheet.write(0, 14, "SOR Rank", bold)
            worksheet.write(0, 15, "Score", bold)
            worksheet.write(0, 16, "P.D", bold)
            worksheet.write(0, 17, "Away", bold)
            worksheet.write(0, 18, "Home", bold)
            worksheet.write(0, 19, "Movement", bold)
            worksheet.write(0, 20, "Wager", bold)
            worksheet.write(0, 21, "Total", bold)
            worksheet.write(0, 22, "Home Cover", bold)            

            index = 1
            c_0_0 = 0
            c_0_1 = 0
            c_33_0 = 0
            c_33_1 = 0
            c_66_0 = 0
            c_66_1 = 0
            c_100_0 = 0
            c_100_1 = 0

            away_0_0 = 0
            away_0_1 = 0
            home_0_0 = 0
            home_0_1 = 0
            move_0_0 = 0
            move_0_1 = 0

            c_away_0_0 = [0,0,0]
            c_away_0_1 = [0,0,0]
            c_away_33_0 = [0,0,0]
            c_away_33_1 = [0,0,0]
            c_away_66_0 = [0,0,0]
            c_away_66_1 = [0,0,0]
            c_away_100_0 = [0,0,0]
            c_away_100_1 = [0,0,0]       

            move_f_33_0 = 0
            move_f_33_1 = 0
            move_f_66_0 = 0
            move_f_66_1 = 0
            move_f_100_0 = 0
            move_f_100_1 = 0

            flag = False
            for spread in spreadArray: 
                if spread['update_day'] == day:                                        
                    # first_A = get_conf(spread['team'])
                    # first_B = get_coll(spread['team'])
                    #if spread['abbr'] is not None:
                    first_A = get_conf(spread['abbr'])
                    if first_A is None:
                        first_A = get_conf1(spread['team'])

                    first_B = get_coll(spread['abbr'])                    
                    if first_B is None:
                        first_B = get_coll1(spread['team'])

                    away_home = ""
                    result = 0        
                    away_30 = ""
                    home_70 = ""
                    sharp = ""
                    wager = ""
                    p_d = ""
                    props = ""
                    cover = ""
                    if index % 3 == 1:            
                        away_home = first_A["o_away"]
                                        
                        try:
                            array = first_A["o_away"].split('-')                   
                            result = round(int(array[0])/(int(array[0])+int(array[1])) * 100)
                        except:
                            result = 0
                            pass
                        
                        if result <= 30:
                            flag = True
                        else:                
                            flag = False

                        props = ""
                        cover = ""
                    else:
                        pro = 0
                        away_home = first_A["o_home"]            

                        result = 0
                        try:
                            array = first_A["o_home"].split('-')
                            result = round(int(array[0])/(int(array[0])+int(array[1])) * 100)                    
                        except:
                            result = 0
                            pass
                        
                        if result >= 70:
                            home_70 = 1                
                        else:                
                            home_70 = 0

                        try:
                            sharp = float(spread['bovada']) - float(spread['bookmarker'])                
                        except:
                            sharp = 0

                        wager = "no"

                        
                        p_d = spread['diff']

                        if flag == True:
                            away_30 = 1

                            if result >= 70 and sharp > 0:
                                wager = "yes"            
                        else:
                            away_30 = 0    

                        if away_30 == 1:
                            pro = pro + 1
                        
                        if home_70 == 1:
                            pro = pro + 1

                        if sharp > 0:
                            pro = pro + 1

                        props = str(round(pro/3*100)) + '%'
                                                
                        try:
                            cover = str(float(p_d) + float(spread['bookmarker']))
                            
                            if pro == 1:    #33%
                                if sharp <= 0:
                                    if float(p_d) + float(spread['bookmarker']) > 0:
                                        move_f_33_0 = move_f_33_0 + 1
                                    else:
                                        move_f_33_1 = move_f_33_1 + 1                                
                            elif pro == 2:  #66
                                if sharp <= 0:
                                    if float(p_d) + float(spread['bookmarker']) > 0:
                                        move_f_66_0 = move_f_66_0 + 1
                                    else:
                                        move_f_66_1 = move_f_66_1 + 1
                                pass
                            elif pro == 3:  #100
                                if sharp <= 0:
                                    if float(p_d) + float(spread['bookmarker']) > 0:
                                        move_f_100_0 = move_f_100_0 + 1
                                    else:
                                        move_f_100_1 = move_f_100_1 + 1
                                pass

                            if float(p_d) + float(spread['bookmarker']) > 0:
                                if pro == 0:
                                    c_0_0 = c_0_0 + 1
                                    
                                    #check away,home,movement
                                    if away_30 == 1:
                                        c_away_0_0[0] = c_away_0_0[0] + 1
                                    else:
                                        c_away_0_1[0] = c_away_0_1[0] + 1

                                    if home_70 == 1:
                                        c_away_0_0[1] = c_away_0_0[1] + 1
                                    else:
                                        c_away_0_1[1] = c_away_0_1[1] + 1

                                    if sharp > 0:
                                        c_away_0_0[2] = c_away_0_0[2] + 1
                                    else:
                                        c_away_0_1[2] = c_away_0_1[2] + 1

                                elif pro == 1:
                                    c_33_0 = c_33_0 + 1

                                    #check away,home,movement
                                    if away_30 == 1:
                                        c_away_33_0[0] = c_away_33_0[0] + 1
                                    else:
                                        c_away_33_1[0] = c_away_33_1[0] + 1

                                    if home_70 == 1:
                                        c_away_33_0[1] = c_away_33_0[1] + 1
                                    else:
                                        c_away_33_1[1] = c_away_33_1[1] + 1

                                    if sharp > 0:
                                        c_away_33_0[2] = c_away_33_0[2] + 1
                                    else:
                                        c_away_33_1[2] = c_away_33_1[2] + 1

                                elif pro == 2:
                                    c_66_0 = c_66_0 + 1

                                    #check away,home,movement
                                    if away_30 == 1:
                                        c_away_66_0[0] = c_away_66_0[0] + 1
                                    else:
                                        c_away_66_1[0] = c_away_66_1[0] + 1

                                    if home_70 == 1:
                                        c_away_66_0[1] = c_away_66_0[1] + 1
                                    else:
                                        c_away_66_1[1] = c_away_66_1[1] + 1

                                    if sharp > 0:
                                        c_away_66_0[2] = c_away_66_0[2] + 1
                                    else:
                                        c_away_66_1[2] = c_away_66_1[2] + 1

                                elif pro == 3:
                                    c_100_0 = c_100_0 + 1

                                    #check away,home,movement
                                    if away_30 == 1:
                                        c_away_100_0[0] = c_away_100_0[0] + 1
                                    else:
                                        c_away_100_1[0] = c_away_100_1[0] + 1

                                    if home_70 == 1:
                                        c_away_100_0[1] = c_away_100_0[1] + 1
                                    else:
                                        c_away_100_1[1] = c_away_100_1[1] + 1

                                    if sharp > 0:
                                        c_away_100_0[2] = c_away_100_0[2] + 1
                                    else:
                                        c_away_100_1[2] = c_away_100_1[2] + 1
                            else:
                                if pro == 0:
                                    c_0_1 = c_0_1 + 1
                                elif pro == 1:
                                    c_33_1 = c_33_1 + 1
                                elif pro == 2:
                                    c_66_1 = c_66_1 + 1
                                elif pro == 3:
                                    c_100_1 = c_100_1 + 1
                                
                        except:
                            cover = ""

                        if away_30 == 1:
                            away_0_1 = away_0_1 + 1
                        else:
                            away_0_0 = away_0_0 + 1

                        if home_70 == 1:
                            home_0_1 = home_0_1 + 1
                        else:
                            home_0_0 = home_0_0 + 1

                        if sharp > 0:
                            move_0_1 = move_0_1 + 1
                        else:
                            move_0_0 = move_0_0 + 1

                    row = list({                        
                        'id': index,
                        'date': format_day,
                        'team': spread['team'],
                        'conf': first_A["conference_name"],
                        'spread': spread['opener'],
                        'spread_odd': spread['opener_odds'],
                        'bookmaker': spread['bookmarker'],
                        'bootmaker_odd': spread['bookmarker_odds'],
                        'fivetime': spread['five_times'],
                        'fivetime_odd': spread['five_times_odds'],
                        'bovada': spread['bovada'],
                        'bovada_odd': spread['bovada_odds'],
                        'away_home': away_home,
                        'percentage': str(result) + "%",
                        'w_l': first_A["o_pct"],
                        'strk': first_A["o_strk"],
                        'bpi_rank': first_B['bpi_rk'],
                        'sos_rank': first_B['sos_rk'],
                        'sor_rank': first_B['sor_rk'],
                        'score': spread['point'],
                        'p_d': p_d,
                        'away_30': str(away_30),
                        'home_70': str(home_70),
                        'sharp': str(sharp),
                        'wager': wager,
                        'update_time': today,
                        'o_away': first_A["o_away"],
                        'o_home': first_A["o_home"],
                        'time': spread['time'],
                        'total': props,
                        'cover': cover
                    }.values())

                    allData.append(row)
                    worksheet.write(index, 0, row[1])
                    worksheet.write(index, 1, row[28])
                    worksheet.write(index, 2, row[2])
                    worksheet.write(index, 3, row[3])
                    #worksheet.write(index, 3, row[4])
                    worksheet.write(index, 4, row[4])

                    if row[6] != row[10]:
                        worksheet.write(index, 5, row[6], magenta_format)
                        worksheet.write(index, 7, row[10], magenta_format)
                    else:
                        worksheet.write(index, 5, row[6])
                        worksheet.write(index, 7, row[10])

                    worksheet.write(index, 6, row[8])
                    worksheet.write(index, 8, row[12])
                    #worksheet.write(index, 8, row[13])                
                    worksheet.write(index, 10, row[14])                    
                    worksheet.write_string(index, 11, row[15])

                    
                    if index % 3 == 1:
                        if float(row[13].replace('%','')) <= 30:
                            worksheet.write(index, 9, row[13], tomato_format2)                        
                        else:
                            worksheet.write(index, 9, row[13])
                    else:
                        if float(row[13].replace('%','')) >= 70:
                            worksheet.write(index, 9, row[13], green_format1)
                        else:
                            worksheet.write(index, 9, row[13])

                    #worksheet.write(index, 12, row[13])
                    worksheet.write(index, 12, row[16]) 
                    worksheet.write(index, 13, row[17])
                    worksheet.write(index, 14, row[18])
                    worksheet.write(index, 15, row[19])
                    worksheet.write(index, 16, row[20])
                    worksheet.write(index, 17, row[21])
                    worksheet.write(index, 18, row[22])
                    worksheet.write(index, 19, row[23])
                    worksheet.write(index, 20, row[24])
                    worksheet.write(index, 21, row[29])
                    worksheet.write(index, 22, row[30])
                    #worksheet.write(index, 25, row[29])
                    #worksheet.write(index, 26, row[30])

                    index = index + 1
                    if index % 3 == 0:
                        index = index + 1


            #write the chart
            total_v = c_0_0+c_33_0+c_66_0+c_100_0+c_0_1+c_33_1+c_66_1+c_100_1

            worksheet.write(0, 25, "Home Cover", bold) 
            worksheet.write(0, 26, "Yes", bold) 
            worksheet.write(0, 27, "No", bold) 
            worksheet.write(0, 28, "Total", bold) 

            worksheet.write(1, 25, "0%", bold) 
            worksheet.write(1, 26, str(c_0_0), bold) 
            worksheet.write(1, 27, str(c_0_1), bold) 
            worksheet.write(1, 28, str(c_0_0+c_0_1), bold) 

            try:
                worksheet.write(2, 26, str(int(c_0_0/total_v*100)) + '%') 
                worksheet.write(2, 27, str(int(c_0_1/total_v*100)) + '%') 
            except:
                worksheet.write(2, 26, '0%') 
                worksheet.write(2, 27, '0%') 
            try:
                worksheet.write(2, 28, str(int((c_0_0+c_0_1)/total_v*100)) + '%') 
            except:
                worksheet.write(2, 28, '0%') 

            worksheet.write(3, 25, "33%", bold) 
            worksheet.write(3, 26, str(c_33_0), bold) 
            worksheet.write(3, 27, str(c_33_1), bold) 
            worksheet.write(3, 28, str(c_33_0+c_33_1), bold) 
            
            try:
                worksheet.write(4, 26, str(int(c_33_0/total_v*100)) + '%') 
                worksheet.write(4, 27, str(int(c_33_1/total_v*100)) + '%') 
            except:
                worksheet.write(4, 26, '0%')
                worksheet.write(4, 27, '0%')

            try:
                worksheet.write(4, 28, str(int((c_33_0+c_33_1)/total_v*100)) + '%') 
            except:
                worksheet.write(4, 28, '0%')

            worksheet.write(5, 25, "Away") 
            worksheet.write(5, 26, str(c_away_33_0[0]), bold) 
            worksheet.write(5, 27, str(c_away_33_1[0]), bold) 
            worksheet.write(5, 28, str(c_away_33_0[0] + c_away_33_1[0]), bold) 

            try:
                worksheet.write(6, 26, str(int(c_away_33_0[0]/total_v*100)) + '%') 
                worksheet.write(6, 27, str(int(c_away_33_1[0]/total_v*100)) + '%') 
            except:
                worksheet.write(6, 26, '0%')
                worksheet.write(6, 27, '0%')

            try:
                worksheet.write(6, 28, str(int((c_away_33_0[0] + c_away_33_1[0])/total_v*100)) + '%')
            except:
                worksheet.write(6, 28, '0%')

            worksheet.write(7, 25, "Home") 
            worksheet.write(7, 26, str(c_away_33_0[1]), bold) 
            worksheet.write(7, 27, str(c_away_33_1[1]), bold) 
            worksheet.write(7, 28, str(c_away_33_0[1] + c_away_33_1[1]), bold) 

            try:
                worksheet.write(8, 26, str(int(c_away_33_0[1]/total_v*100)) + '%') 
                worksheet.write(8, 27, str(int(c_away_33_1[1]/total_v*100)) + '%') 
            except:
                worksheet.write(8, 26, '0%')
                worksheet.write(8, 27, '0%')

            try:
                worksheet.write(8, 28, str(int((c_away_33_0[1] + c_away_33_1[1])/total_v*100)) + '%')
            except:
                worksheet.write(8, 28, '0%')

            worksheet.write(9, 25, "Movement") 
            worksheet.write(9, 26, str(c_away_33_0[2]), bold) 
            worksheet.write(9, 27, str(c_away_33_1[2]), bold) 
            worksheet.write(9, 28, str(c_away_33_0[2] + c_away_33_1[2]), bold) 

            try:
                worksheet.write(10, 26, str(int(c_away_33_0[2]/total_v*100)) + '%') 
                worksheet.write(10, 27, str(int(c_away_33_1[2]/total_v*100)) + '%') 
            except:
                worksheet.write(10, 26, '0%')
                worksheet.write(10, 27, '0%')
            
            try:
                worksheet.write(10, 28, str(int((c_away_33_0[2] + c_away_33_1[2])/total_v*100)) + '%')
            except:
                worksheet.write(10, 28, '0%')

            worksheet.write(11, 25, "66%", bold) 
            worksheet.write(11, 26, str(c_66_0), bold) 
            worksheet.write(11, 27, str(c_66_1), bold) 
            worksheet.write(11, 28, str(c_66_0+c_66_1), bold) 

            try:
                worksheet.write(12, 26, str(int(c_66_0/total_v*100)) + '%') 
                worksheet.write(12, 27, str(int(c_66_1/total_v*100)) + '%') 
            except:
                worksheet.write(12, 26, '0%')
                worksheet.write(12, 27, '0%')

            try:
                worksheet.write(12, 28, str(int((c_66_0+c_66_1)/total_v*100)) + '%') 
            except:
                worksheet.write(12, 28, '0%')

            worksheet.write(13, 25, "Away") 
            worksheet.write(13, 26, str(c_away_66_0[0]), bold) 
            worksheet.write(13, 27, str(c_away_66_1[0]), bold) 
            worksheet.write(13, 28, str(c_away_66_0[0] + c_away_66_1[0]), bold) 

            try:
                worksheet.write(14, 26, str(int(c_away_66_0[0]/total_v*100)) + '%') 
                worksheet.write(14, 27, str(int(c_away_66_1[0]/total_v*100)) + '%') 
            except:
                worksheet.write(14, 26, '0%')
                worksheet.write(14, 27, '0%')
            
            try:
                worksheet.write(14, 28, str(int((c_away_66_0[0] + c_away_66_1[0])/total_v*100)) + '%')
            except:
                worksheet.write(14, 28, '0%')

            worksheet.write(15, 25, "Home") 
            worksheet.write(15, 26, str(c_away_66_0[1]), bold) 
            worksheet.write(15, 27, str(c_away_66_1[1]), bold) 
            worksheet.write(15, 28, str(c_away_66_0[1] + c_away_66_1[1]), bold) 

            try:
                worksheet.write(16, 26, str(int(c_away_66_0[1]/total_v*100)) + '%') 
                worksheet.write(16, 27, str(int(c_away_66_1[1]/total_v*100)) + '%') 
            except:
                worksheet.write(16, 26, '0%')
                worksheet.write(16, 27, '0%')

            try:
                worksheet.write(16, 28, str(int((c_away_66_0[1] + c_away_66_1[1])/total_v*100)) + '%')
            except:
                worksheet.write(16, 28, '0%')

            worksheet.write(17, 25, "Movement") 
            worksheet.write(17, 26, str(c_away_66_0[2]), bold) 
            worksheet.write(17, 27, str(c_away_66_1[2]), bold) 
            worksheet.write(17, 28, str(c_away_66_0[2] + c_away_66_1[2]), bold) 

            try:
                worksheet.write(18, 26, str(int(c_away_66_0[2]/total_v*100)) + '%') 
                worksheet.write(18, 27, str(int(c_away_66_1[2]/total_v*100)) + '%') 
            except:
                worksheet.write(18, 26, '0%')
                worksheet.write(18, 27, '0%')

            try:
                worksheet.write(18, 28, str(int((c_away_66_0[2] + c_away_66_1[2])/total_v*100)) + '%')
            except:
                worksheet.write(18, 28, '0%')            

            worksheet.write(19, 25, "100%", bold) 
            worksheet.write(19, 26, str(c_100_0), bold) 
            worksheet.write(19, 27, str(c_100_1), bold) 
            worksheet.write(19, 28, str(c_100_0+c_100_1), bold) 

            try:
                worksheet.write(20, 26, str(int(c_100_0/(c_100_0+c_100_1)*100)) + '%') 
                worksheet.write(20, 27, str(int(c_100_1/(c_100_0+c_100_1)*100)) + '%') 
            except:
                worksheet.write(20, 26, '0%')
                worksheet.write(20, 27, '0%')

            try:
                worksheet.write(20, 28, str(int((c_100_0+c_100_1)/total_v*100)) + '%') 
            except:
                worksheet.write(20, 28, '0%')

            worksheet.write(21, 25, "Total", bold) 
            worksheet.write(21, 26, str(c_0_0+c_33_0+c_66_0+c_100_0), bold) 
            worksheet.write(21, 27, str(c_0_1+c_33_1+c_66_1+c_100_1), bold) 
            worksheet.write(21, 28, str(c_0_0+c_33_0+c_66_0+c_100_0+c_0_1+c_33_1+c_66_1+c_100_1), bold) 

            try:
                worksheet.write(22, 26, str(int((c_0_0+c_33_0+c_66_0+c_100_0)/total_v*100)) + '%') 
                worksheet.write(22, 27, str(int((c_0_1+c_33_1+c_66_1+c_100_1)/total_v*100)) + '%')             
            except:
                worksheet.write(22, 26, '0%')
                worksheet.write(22, 27, '0%')

            #write below chart
            worksheet.write(25, 26, "Home Cover", bold) 

            worksheet.write(26, 25, "False Positive", bold) 
            worksheet.write(26, 26, "Yes", bold) 
            worksheet.write(26, 27, "No", bold) 

            
            worksheet.write(27, 25, "33%", bold) 
            worksheet.write(27, 26, str(move_f_33_0), bold) 
            worksheet.write(27, 27, str(move_f_33_1), bold) 
           
            worksheet.write(28, 25, "66%", bold) 
            worksheet.write(28, 26, str(move_f_66_0), bold) 
            worksheet.write(28, 27, str(move_f_66_1), bold) 

            worksheet.write(29, 25, "100%", bold) 
            worksheet.write(29, 26, str(move_f_100_0), bold) 
            worksheet.write(29, 27, str(move_f_100_1), bold) 

            worksheet.write(30, 25, "Total", bold) 
            worksheet.write(30, 26, str(move_f_33_0 + move_f_66_0 + move_f_100_0), bold) 
            worksheet.write(30, 27, str(move_f_33_1 + move_f_66_1 + move_f_100_1), bold) 
                  
        print("Making weekTotal...")        
        worksheet = workbook.add_worksheet("Weekly Total")
        worksheet.write(0, 0, "Date", bold)
        worksheet.write(0, 1, "Time", bold)
        worksheet.write(0, 2, "Matchcup", bold)
        worksheet.write(0, 3, "Result", bold)
        worksheet.write(0, 4, "P.D", bold)
        worksheet.write(0, 5, "Bookmaker", bold)
        worksheet.write(0, 6, "Wager", bold)
        #worksheet.write(0, 6, "Away", bold)
        #worksheet.write(0, 7, "Home", bold)
        #worksheet.write(0, 8, "Wager", bold)
        #worksheet.write(0, 9, "Bookmaker-P.D", bold)
        worksheet.write(0, 7, "Away", bold)
        worksheet.write(0, 8, "Home", bold)
        worksheet.write(0, 9, "Movement", bold)
        worksheet.write(0, 10, "Total", bold)
        worksheet.write(0, 11, "Home Cover", bold)
        worksheet.write(0, 12, "Result", bold)

        index = 1
        below_0 = [0,0,0]
        below_1 = [0,0,0]
        above_0 = [0,0,0]
        above_1 = [0,0,0]
        array = [-15,-14.5,-14,-13.5,-13,-12.5,-12,-11.5,-11,-10.5,-10,-9.5,-9,-8.5,-8,-7.5,-7,-6.5,-6,-5.5,-5,-4.5,-4,-3.5,-3,-2.5,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10,10.5,11,11.5,12,12.5,13,13.5,14,14.5,15]
        array_c_0 = [0] * 61
        array_c_1 = [0] * 61
        for tindex in range(int(len(allData)/2)):
            row = allData[tindex*2]
            nrow = allData[tindex*2 + 1]
            if nrow[29] == "67%" or nrow[29] == "100%":
                
                worksheet.write(index, 0, row[1])   #Date
                worksheet.write(index, 1, row[28])   #Time
                worksheet.write(index, 2, row[2])   #Matchcup
                worksheet.write(index, 3, row[19])   #Result
                worksheet.write(index, 4, row[20])   #P.D
                worksheet.write(index, 5, row[6])   #Bookmaker
                worksheet.write(index, 6, row[24])   #Away Record
                #worksheet.write(index, 7, row[27])   #Home Record
                #worksheet.write(index, 6, row[24])   #Wager
                #worksheet.write(index, 9, row[23])   #Bookmaker-P.D
                worksheet.write(index, 7, row[21])
                worksheet.write(index, 8, row[22])
                worksheet.write(index, 9, row[23])                
                worksheet.write(index, 10, row[29])
                worksheet.write(index, 11, row[30])
                
                #worksheet.write(index, 12, row[30])

                worksheet.write(index+1, 0, nrow[1])   #Date
                worksheet.write(index+1, 1, nrow[28])   #Time
                worksheet.write(index+1, 2, nrow[2])   #Matchcup
                worksheet.write(index+1, 3, nrow[19])   #Result
                worksheet.write(index+1, 4, nrow[20])   #P.D
                worksheet.write(index+1, 5, nrow[6])   #Bookmaker
                #worksheet.write(index+1, 6, nrow[26])   #Away Record
                #worksheet.write(index+1, 7, nrow[27])   #Home Record
                worksheet.write(index+1, 6, nrow[24])   #Wager
                #worksheet.write(index+1, 9, nrow[23])   #Bookmaker-P.D

                worksheet.write(index+1, 7, nrow[21])
                worksheet.write(index+1, 8, nrow[22])
                worksheet.write(index+1, 9, nrow[23])                
                worksheet.write(index+1, 10, nrow[29])
                worksheet.write(index+1, 11, nrow[30])

                bookmaker = float(nrow[6])
                if float(nrow[30]) > 0:
                    worksheet.write(index+1, 12, 1)

                    if bookmaker > 15:
                        if bookmaker >= 15.5 and bookmaker <= 20:
                            above_0[0] = above_0[0] + 1
                        elif bookmaker >= 20.5 and bookmaker <= 25:
                            above_0[1] = above_0[1] + 1
                        elif bookmaker >= 25.5 and bookmaker <= 30:
                            above_0[2] = above_0[2] + 1

                    elif bookmaker<-15:
                        if bookmaker >= -30 and bookmaker <= -25.5:
                            below_0[0] = below_0[0] + 1
                        elif bookmaker >= -25 and bookmaker <= -20.5:
                            below_0[1] = below_0[1] + 1
                        elif bookmaker >= -20 and bookmaker <= -15.5:
                            below_0[2] = below_0[2] + 1


                    else:
                        for i in range(len(array)):
                            if float(array[i]) == bookmaker:
                                array_c_0[i] = array_c_0[i] + 1
                                break
                else:
                    worksheet.write(index+1, 12, 0)

                    if bookmaker > 15:
                        if bookmaker >= 15.5 and bookmaker <= 20:
                            above_1[0] = above_1[0] + 1
                        elif bookmaker >= 20.5 and bookmaker <= 25:
                            above_1[1] = above_1[1] + 1
                        elif bookmaker >= 25.5 and bookmaker <= 30:
                            above_1[2] = above_1[2] + 1

                    elif bookmaker<-15:
                        if bookmaker >= -30 and bookmaker <= -25.5:
                            below_1[0] = below_1[0] + 1
                        elif bookmaker >= -25 and bookmaker <= -20.5:
                            below_1[1] = below_1[1] + 1
                        elif bookmaker >= -20 and bookmaker <= -15.5:
                            below_1[2] = below_1[2] + 1
                    else:
                        for i in range(len(array)):
                            if float(array[i]) == bookmaker:
                                array_c_1[i] = array_c_1[i] + 1
                                break

                index = index + 2
                if index % 3 == 0:
                    index = index + 1

        worksheet.write(0, 14, "Points", bold)
        worksheet.write(0, 15, "Y", bold)
        worksheet.write(0, 16, "N", bold)
        worksheet.write(0, 17, "Total", bold)

        worksheet.write(1, 14, "-25.5-30")

        if below_0[0] != 0:
            worksheet.write(1, 15, str(below_0[0]))

        if below_1[0] != 0:
            worksheet.write(1, 16, str(below_1[0]))

        if below_0[0] + below_1[0] != 0:
            worksheet.write(1, 17, str(below_0[0]+below_1[0]))


        worksheet.write(2, 14, "-20.5-25")

        if below_0[1] != 0:
            worksheet.write(2, 15, str(below_0[1]))

        if below_1[1] != 0:
            worksheet.write(2, 16, str(below_1[1]))

        if below_0[1] + below_1[1] != 0:
            worksheet.write(2, 17, str(below_0[1]+below_1[1]))


        worksheet.write(3, 14, "-15.5-20")

        if below_0[2] != 0:
            worksheet.write(3, 15, str(below_0[2]))

        if below_1[2] != 0:
            worksheet.write(3, 16, str(below_1[2]))

        if below_0[2] + below_1[2] != 0:
            worksheet.write(3, 17, str(below_0[2]+below_1[2]))

        for i in range(len(array)):
            worksheet.write(i+4, 14, str(array[i]))
            if array_c_0[i] != 0:
                worksheet.write(i+4, 15, str(array_c_0[i]))

            if array_c_1[i] != 0:
                worksheet.write(i+4, 16, str(array_c_1[i]))

            if array_c_0[i]+array_c_1[i] != 0:
                worksheet.write(i+4, 17, str(array_c_0[i]+array_c_1[i]))

        
        worksheet.write(len(array)+4, 14, "15.5-20")

        if above_0[0] != 0:
            worksheet.write(len(array)+4, 15, str(above_0[0]))

        if above_1 != 0:
            worksheet.write(len(array)+4, 16, str(above_1[0]))

        if above_0[0]+above_1[0] != 0:
            worksheet.write(len(array)+4, 17, str(above_0[0]+above_1[0]))

        worksheet.write(len(array)+5, 14, "20.5-25")

        if above_0[1] != 0:
            worksheet.write(len(array)+5, 15, str(above_0[1]))

        if above_1[1] != 0:
            worksheet.write(len(array)+5, 16, str(above_1[1]))

        if above_0[1]+above_1[1] != 0:
            worksheet.write(len(array)+5, 17, str(above_0[1]+above_1[1]))

        worksheet.write(len(array)+6, 14, "25.5-30")

        if above_0[2] != 0:
            worksheet.write(len(array)+6, 15, str(above_0[2]))

        if above_1[2] != 0:
            worksheet.write(len(array)+6, 16, str(above_1[2]))

        if above_0[2]+above_1[2] != 0:
            worksheet.write(len(array)+6, 17, str(above_0[2]+above_1[2]))

        workbook.close()
    except Exception as e:
        logging.info(str(e))
        pass

def main():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ncaa.log')
    logging.basicConfig(filename=filename,level=logging.INFO,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',)
    logging.info("Start...")
    logging.info("Espn...")
    get_espn()

    logging.info("colleage...")
    get_colleage()

    logging.info("spread...")
    weekday = findDay()

    for i in range(weekday+1):                
        findex = weekday -i
        day = datetime.strftime(datetime.now() - timedelta(findex), '%Y%m%d')
        spread = get_spread()
        spread.automate(day)    

    logging.info("creating...")
    make_spread()       
    
    
main()
