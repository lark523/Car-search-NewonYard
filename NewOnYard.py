import pprint, ssl, re, sqlite3
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import time, sys, csv
from CreateDB import CreateDB

def loadCars(currentDB):
    dataToLoad = input("Please provide the name of the html file in this format: carlist.html \n")
    #numOfFiles = len(sys.argv)
    #print("Num of files", numOfFiles)

    with open( dataToLoad,'r') as f:
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
                    #print(car)
                    #print(count)
                    #print(Categories[count])
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
    outputcsv = input("Provide the name of the output file e.g. 'results.csv': \n")
    with open(outputcsv, 'w', newline = '') as outputfile:
        outputwriter = csv.writer(outputfile, delimiter=',',quotechar = ' ', skipinitialspace = True)
        outputwriter.writerow(['ID','MAKE','MODEL','YEAR', 'LOCATION','ROW','YARDDATE','VIN','PARTS'])
        with open(csvfile, newline = '') as filetoread:
            partslist = csv.reader(filetoread, delimiter = ',')
            for row in partslist:
                if len(row)>0:

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
                        #print("No matches found for ",', '.join(row))
                        continue
                    else:
                        for element in results:
                            for term in element:
                                outputfile.write(str(term))
                                outputfile.write(',')
                            outputfile.write(parts)
                            outputfile.write('\n')
                            print((element, parts))
            print("\n")
    outputfile.close()
    filetoread.close()


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
            loadCars(newDB)
            continue

        if select == '3':
            #inputFile = input("Enter the name of the csv file to be used \n")
            while True:
                try:
                    inputFile = input("Enter the name of the csv file to be used e.g. 'parts.csv' or enter  'x' to exit \n")
                    if inputFile.endswith('.csv'):
                        open(inputFile, 'r')
                        break
                    else:
                        if inputFile == 'x':
                            return
                        else: print("Not a valid file, please try again")
                except:
                    print(f'{inputFile}  could not be found. Please try again... \n ') 
            newDB.cur.execute('''SELECT DISTINCT Location from Cars''')
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
            continue
        
        else:
            return
              




if __name__ == '__main__':
    main()
        



