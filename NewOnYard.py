import pprint, ssl, re, sqlite3
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import time, sys, csv
from CreateDB import CreateDB

def main():
    while True:
        select = input("Enter 1: Load car data into a brand new database \n 2: Load car data into existing database \n 3: Search car inventory \n")
        dBName = input("Enter the name of the sqlite file that will be used \n")
        newDB = CreateDB(dBName)

        if select == '1':      
            newDB.dbInitialize()
            loadCars(newDB)

        if select == '2':
            loadCars(newDB)

        if select == '3':
            inputFile = input("Enter the name of the csv file to be used \n")
            #try:
            #    inputFile = input("Enter the name of the csv file to be used \n")
            #    open(inputFile, 'r')
            #except: 
            newDB.cur.execute('''SELECT DISTINCT Location from cars''')
            locList = newDB.cur.fetchall()
            locationDic = {}
            locationCount = 1
            print("Select the yard location to search: \n")
            for availableLoc in locList:
                print(f'{locationCount}: {availableLoc[0]}')
                locationDic[str(locationCount)] = availableLoc[0]
                locationCount +=1
            temp = input()
            location_input = locationDic[temp]
            
            idParts(inputFile, newDB,location_input)

        else:
            return

def loadCars(currentDB):

    numOfFiles = len(sys.argv)
    print("Num of files", numOfFiles)

    for x in range(1,numOfFiles):
        print(sys.argv[x])
        with open( sys.argv[x],'r') as f:
            html_doc = f.read()
        car_dict= {}
        Car_list = []
        Categories = ['Year', 'Make', 'Model','Yard Date', 'Row','VIN']

        soup = BeautifulSoup(html_doc, 'html.parser')
        location = soup.find_all(style="float: left;")
        for loc in location:
            if len(loc.select("h2"))>0:
                yard_loc = (loc.select("h2"))[0].string
        li_tags = soup.find_all(class_="fl-table")
        car_count = 0
        for tags in li_tags:
            car_tags = tags.select(("div.cell-content"))
            count = 0
            flag = 0
            for car in car_tags:
                y = list(car.attrs.keys())
                x = list(car.attrs.values())
                if y[0] == "class":
                    if len(x[0]) == 2 and x[0][1] == "mobile":
                        continue
                    else:
                        flag = 1
                        print(car)
                        print(count)
                        print(Categories[count])
                        if count != 5:
                            car_dict[Categories[count]]= car.text
                        if count == 5:
                            vin_num = list(car.find(class_ = "button yellow").attrs.values())[1].split(',')[3]
                            car_dict[Categories[count]] = vin_num
                count +=1
            if flag == 1:

                temp_make = car_dict['Make']
                temp_model = car_dict['Model']
                temp_year = car_dict['Year']
                temp_row = car_dict['Row']
                temp_date = car_dict['Yard Date']
                temp_vin = car_dict['VIN']

                print("         ", car_dict)

                try:
                    currentDB.cur.execute('''INSERT INTO Cars (make, model, year, location, row, yard_date, vin) VALUES (?, ?, ?, ?, ?,?,?)''',
                    (temp_make, temp_model, temp_year, yard_loc, temp_row, temp_date, temp_vin) )
                    car_count +=1
                except sqlite3.IntegrityError:
                    print("A duplicate entry was found")

            currentDB.conn.commit()
        print("\n")
        #print("Data retrieved from ", sys.argv[x])
        print("%d cars were added to the database" % car_count)

def idParts(csvfile, currentDB, location):

    #conn = sqlite3.connect(currentDB.dbName +'.sqlite')
    #cur = conn.cursor()
    with open(csvfile, newline = '') as filetoread:
        partslist = csv.reader(filetoread, delimiter = ',')
        for row in partslist:

            make_sel = row[0]
            model_sel = row[1]
            min_year = row[2].split('-')[0]
            max_year = row[2].split('-')[1]
            parts = row[3]
            #print(make_sel.upper(), model_sel.upper(), min_year, max_year)
            currentDB.cur.execute('''SELECT * FROM Cars WHERE make = ? and model like ? and year >= ? and year <= ? and location = ?''',
                (make_sel.upper(),'%'+ model_sel.upper()+'%', min_year, max_year, location, ) )
            results = currentDB.cur.fetchall()
            #print(results)

            if results == []:
                print("No matches found for ",', '.join(row))
                
            else:
                for element in results:
                    print(element, parts)
        print("\n")


                




if __name__ == '__main__':
    main()
        



