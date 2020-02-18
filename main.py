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
                try:
                    length = len(divs.find_elements_by_xpath("./div"))
                    if length >= 2 and bettingDate is not None:                        
                        
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
                            'team' : teams[i].text,
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
                            'team' : teams[i+1].text,
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
            day = datetime.strftime(datetime.now() - timedelta(findex), '%Y%m%d')   
            date = datetime.strftime(datetime.now() - timedelta(findex), '%d')
            month = datetime.strftime(datetime.now() - timedelta(findex), '%b')

            worksheet = workbook.add_worksheet(month + '.' + date)

            worksheet.write(0, 0, "Date", bold)
            worksheet.write(0, 1, "Team", bold)
            worksheet.write(0, 2, "Conf", bold)
            worksheet.write(0, 3, "Spread (Opener)", bold)
            worksheet.write(0, 4, "Odds", bold)
            worksheet.write(0, 5, "Spread (BookMaker)", bold)
            worksheet.write(0, 6, "Odds", bold)
            worksheet.write(0, 7, "Spread (5 Dimes)", bold)
            worksheet.write(0, 8, "Odds", bold)
            worksheet.write(0, 9, "Spread (Bovada)", bold)
            worksheet.write(0, 10, "Odds", bold)
            worksheet.write(0, 11, "Away/Home Overall Record", bold)
            worksheet.write(0, 12, "Percentage", bold)
            worksheet.write(0, 13, "W-L (Overall) PCT", bold)
            worksheet.write(0, 14, "STRK", bold)
            worksheet.write(0, 15, "BPI Rank", bold)
            worksheet.write(0, 16, "SOS Rank", bold)
            worksheet.write(0, 17, "SOR Rank", bold)
            worksheet.write(0, 18, "Score", bold)
            worksheet.write(0, 19, "P.D", bold)
            worksheet.write(0, 20, "Away 30% below", bold)
            worksheet.write(0, 21, "Home 70% above", bold)
            worksheet.write(0, 22, "Sharp-Square", bold)
            worksheet.write(0, 23, "Wager", bold)            

            index = 1
            flag = False
            for spread in spreadArray: 
                if spread['update_day'] == day:
                    first_A = get_conf(spread['team'])
                    first_B = get_coll(spread['team'])

                    away_home = ""
                    result = 0        
                    away_30 = ""
                    home_70 = ""
                    sharp = ""
                    wager = ""
                    p_d = ""

                    if spread['diff'] > 0:
                        p_d = spread['diff']

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
                    else:
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
                        if flag == True:
                            away_30 = 1

                            if result >= 70 and sharp > 0:
                                wager = "yes"            
                        else:
                            away_30 = 0    

                    row = list({
                        'id': index,
                        'date': spread['date'],
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
                    }.values())

                    allData.append(row)
                    worksheet.write(index, 0, row[1])
                    worksheet.write(index, 1, row[2])
                    worksheet.write(index, 2, row[3])
                    worksheet.write(index, 3, row[4])
                    worksheet.write(index, 4, row[5])

                    if row[6] != row[10]:
                        worksheet.write(index, 5, row[6], magenta_format)
                        worksheet.write(index, 9, row[10], magenta_format)
                    else:
                        worksheet.write(index, 5, row[6])
                        worksheet.write(index, 9, row[10])

                    worksheet.write(index, 6, row[7])
                    worksheet.write(index, 7, row[8])
                    worksheet.write(index, 8, row[9])                
                    worksheet.write(index, 10, row[11])
                    
                    worksheet.write_string(index, 11, row[12])

                    
                    if index % 3 == 1:
                        if float(row[13].replace('%','')) <= 30:
                            worksheet.write(index, 12, row[13], tomato_format2)                        
                        else:
                            worksheet.write(index, 12, row[13])
                    else:
                        if float(row[13].replace('%','')) >= 70:
                            worksheet.write(index, 12, row[13], green_format1)
                        else:
                            worksheet.write(index, 12, row[13])

                    #worksheet.write(index, 12, row[13])
                    worksheet.write(index, 13, row[14])
                    worksheet.write(index, 14, row[15])
                    worksheet.write(index, 15, row[16])
                    worksheet.write(index, 16, row[17])
                    worksheet.write(index, 17, row[18])
                    worksheet.write(index, 18, row[19])
                    worksheet.write(index, 19, row[20])
                    worksheet.write(index, 20, row[21])
                    worksheet.write(index, 21, row[22])
                    worksheet.write(index, 22, row[23])
                    worksheet.write(index, 23, row[24])

                    index = index + 1
                    if index % 3 == 0:
                        index = index + 1

               
        print("Making weekTotal...")        
        worksheet = workbook.add_worksheet("Weekly Total")
        worksheet.write(0, 0, "Date", bold)
        worksheet.write(0, 1, "Matchcup", bold)
        worksheet.write(0, 2, "Result", bold)
        worksheet.write(0, 3, "P.D", bold)
        worksheet.write(0, 4, "Bookmaker", bold)
        worksheet.write(0, 5, "Away Record", bold)
        worksheet.write(0, 6, "Home Record", bold)
        worksheet.write(0, 7, "Wager", bold)
        worksheet.write(0, 8, "Bookmaker-P.D", bold)
        
        index = 1
                             
        for tindex in range(int(len(allData)/2)):
            row = allData[tindex*2]
            nrow = allData[tindex*2 + 1]
            if nrow[24] == "yes":
                
                worksheet.write(index, 0, row[1])   #Date
                worksheet.write(index, 1, row[2])   #Matchcup
                worksheet.write(index, 2, row[19])   #Result
                worksheet.write(index, 3, row[20])   #P.D
                worksheet.write(index, 4, row[6])   #Bookmaker
                worksheet.write(index, 5, row[26])   #Away Record
                worksheet.write(index, 6, row[27])   #Home Record
                worksheet.write(index, 7, row[24])   #Wager
                worksheet.write(index, 8, row[23])   #Bookmaker-P.D
                            
                worksheet.write(index+1, 0, nrow[1])   #Date
                worksheet.write(index+1, 1, nrow[2])   #Matchcup
                worksheet.write(index+1, 2, nrow[19])   #Result
                worksheet.write(index+1, 3, nrow[20])   #P.D
                worksheet.write(index+1, 4, nrow[6])   #Bookmaker
                worksheet.write(index+1, 5, nrow[26])   #Away Record
                worksheet.write(index+1, 6, nrow[27])   #Home Record
                worksheet.write(index+1, 7, nrow[24])   #Wager
                worksheet.write(index+1, 8, nrow[23])   #Bookmaker-P.D

                index = index + 2
                if index % 3 == 0:
                    index = index + 1

        workbook.close()
    except Exception as e:
        logging.info(str(e))
        pass

def main():
    # for handler in logging.root.handlers[:]:
    #     logging.root.removeHandler(handler)
    # filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ncaa.log')
    # logging.basicConfig(filename=filename,level=logging.INFO,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',)
    # logging.info("Start...")
    # logging.info("Espn...")
    # get_espn()

    # logging.info("colleage...")
    # get_colleage()

    # logging.info("spread...")
    # weekday = findDay()

    # for i in range(weekday+1):                
    #     findex = weekday -i
    #     day = datetime.strftime(datetime.now() - timedelta(findex), '%Y%m%d')
    #     spread = get_spread()
    #     spread.automate(day)    

    # logging.info("creating...")
    # make_spread()    
    
    # logging.info("End...")    
    # print(SequenceMatcher(None, "Boston University Terriers".lower(), "Bryant University".lower()).ratio())
    # print(SequenceMatcher(None, "Bryant Bulldogs".lower(), "Bryant University".lower()).ratio())

    # print(SequenceMatcher(None, "Bryant".lower(), "Bryant".lower()).ratio())
    
    # print("Getting the Telemundo News...............................")
    # url = 'https://www.telemundo.com/noticias'
        
    # branch_id = 2
    # update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # pageString = requests.get(url).text
    # pattern = re.compile("\"front\":{(.*?)},\"layout\"")
    # data = pattern.findall(pageString)
    # result = json.loads('{' + data[0] + '}')
    # print(result)
    # articleData = []
    # for item in result["curation"]["layouts"][0]["packages"][0]["items"]:
    #     articleData.append({
    #         "subType": item["type"],
    #         "link": item["computedValues"]["url"],
    #         "thumbnail": item["computedValues"]["teaseImage"]["url"]["primary"],
    #         "title": item["computedValues"]["headline"],
    #         "branch_id": branch_id,
    #         "update_time": update_time
    #     })  

    # print(articleData)
    # print("Getting the Univision News...............................")
    # url = 'https://www.univision.com/proxy/api/cached/web-app-state?url=https://www.univision.com/noticias'
    
    # subType = "article"
    # branch_id = 1
    # update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # pageString = requests.get(url).text
    
    # result = json.loads(pageString)
    
    # articleData = []
    # for section in result['data']['page']['data']['widgets'][0]['contents']:
        
    #     articleData.append({
    #         "title": section['title'],
    #         "thumbnail": section['image']['renditions']['original']['href'],
    #         "link": section['uri'],
    #         "subType": section['type'],
    #         "branch_id": branch_id,
    #         "update_time": update_time
    #     })

    a = [1]
    for i in range(len(a)):
        print(a[i])
        print(a[len(a)-i-1])

main()
