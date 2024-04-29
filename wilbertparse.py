import pprint, ssl, re, sqlite3
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import datetime, sys, csv, re
from CreateDB import CreateDB

def main():
    dBName = input("Enter the name of the sqlite file that will be used (exclude the .sqlite)\n")
    newDB = CreateDB(dBName)

    while True:
        print("\n ____Main Menu______")
        select = input("Enter '1' to create a brand new database \n      '2' to Load car data into database \n      '3' to search car inventory \n      Any other character will exit the program\n")

        if select == '1':      
            newDB.dbInitialize()
            continue
            
        if select == '2':
            parseData(newDB)

        else:
            return

def parseData(name_of_DB):
    with open ('wilbert.txt', 'r',newline = '') as inputfile:
        #linelist = inputfile.readlines()
        lines = inputfile.read()
        #print(lines)
        car_list = []
        count = 0
        m = re.findall('([12][0-9][0-9][0-9](.*\s)+?[D][a][y][s].+)',lines)
        #m = re.search('[2][0-9][0-9][0-9]',lines)
        #print(type(m))
        #print(len(m))
        for item in m:
            #print(item[0])
            #print("\n")
            itemslist = item[0].split('\n')  #Tuple is returned
            #print(itemslist)
            #print('\n')

            car_dict={}
            itemmax = len(itemslist)
            car_dict['Year'] = itemslist[0].split(' ')[0]
            car_dict['Make'] = itemslist[0].split(' ')[1]
            car_dict['Model'] =(' ').join(itemslist[0].split(' ')[2:])
            car_dict['VIN'] = itemslist[1].split(' ')[1]
            car_dict['Row'] = itemslist[itemmax-2].split(' ')[2]
            car_dict['Location'] = itemslist[itemmax-2].split(' ')[0]
            car_dict['Yard Date'] = (datetime.date.today() - datetime.timedelta(days=int(itemslist[itemmax-1].split(' ')[3]))).strftime("%m/%d/%y")

            #print(datetime.date.today().strftime("%m/%d/%y"))

            car_list.append(car_dict)


        #print(car_list)


    inputfile.close()

    for car in car_list:
        temp_make = car['Make']
        temp_model = car['Model']
        temp_year = car['Year']
        temp_row = car['Row']
        temp_date = car['Yard Date']
        temp_vin = car['VIN']
        temp_loc = car['Location']
        
        print("         ", car)

        try:
            name_of_DB.cur.execute('''INSERT INTO Cars (make, model, year, location, row, yard_date, vin) VALUES (?, ?, ?, ?, ?,?,?)''',
            (temp_make, temp_model, temp_year, temp_loc, temp_row, temp_date, temp_vin) )
            count +=1
        except sqlite3.IntegrityError:
            print("A duplicate entry was found")

        name_of_DB.conn.commit()
    
    print("\n")
    print("%d cars were added to the database" % count)


if __name__ == '__main__':
    main()
        


