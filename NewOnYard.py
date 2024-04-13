import pprint, ssl, re, sqlite3
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import time
from CreateDB import CreateDB
import sys

def main():
    select = input("Enter 1: Load car data into a brand new database \n 2: Load car data into existing database \n 3: Remove car data \n")
    dBName = input("Enter the name of the sqlite file that will be used \n")
    newDB = CreateDB(dBName)
    
    if select == '1':      
        newDB.dbInitialize()
        loadCars(newDB)

    if select == '2':
        loadCars(newDB)

    if select == '3':
        pass

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
        Categories = ['Year', 'Make', 'Model','Yard Date', 'Location', 'VIN']

        soup = BeautifulSoup(html_doc, 'html.parser')
        location = soup.find_all(style="float: left;")
        for loc in location:
            if len(loc.select("h2"))>0:
                yardloc = (loc.select("h2"))[0].string
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
                        #print(car)
                        if count != 5 and count !=4:
                            car_dict[Categories[count]]= car.text
                        if count == 4:
                            car_dict[Categories[count]] = yardloc
                        if count == 5:
                            vin_num = list(car.find(class_ = "button yellow").attrs.values())[1].split(',')[3]
                            car_dict[Categories[count]] = vin_num
                count +=1
            if flag == 1:

                temp_make = car_dict['Make']
                temp_model = car_dict['Model']
                temp_year = car_dict['Year']
                temp_location = car_dict['Location']
                temp_date = car_dict['Yard Date']
                temp_vin = car_dict['VIN']

                print("         ", car_dict)

                try:
                    currentDB.cur.execute('''INSERT INTO Cars (make, model, year, location, yard_date, vin) VALUES (?, ?, ?, ?, ?,?)''',
                    (temp_make, temp_model, temp_year, temp_location, temp_date, temp_vin) )
                    car_count +=1
                except sqlite3.IntegrityError:
                    #status = car_compare(temp_make, temp_model, temp_year, temp_location, temp_date, temp_vin)
                    print("A duplicate entry was found")

            currentDB.conn.commit()
        print("\n")
        #print("Data retrieved from ", sys.argv[x])
        print("%d cars were added to the database" % car_count)



if __name__ == '__main__':
    main()
        



