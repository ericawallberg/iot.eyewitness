################################################################################
##                            IoT.EYEWITNESS                                  ##
##                             db_setup.py                                    ##   
##  SCRIPT TO EXTRACT ARTIFACTS FROM A SPECIFIED FOLDER                       ##
## "Usage: python db_setup [--help] | case_name artifacts_folder_path]"       ##
################################################################################

#import mysql.connector
from xml.dom.minidom import Element
from numpy import empty
import pandas as pd
from sqlalchemy import column, create_engine, null
import os
import tcxparser
from tcxreader.tcxreader import TCXReader, TCXTrackPoint
import sys
import dataclasses
from typing import List, Any
import MySQLdb
import glob
import xlrd
import inspect
import json
import enum
from datetime import date
from datetime import datetime


USAGE = f"Usage: python {sys.argv[0]} [--help] | case_name artifacts_folder_path]"

def Main(args):

  case_name = args[0]
  folder_path = args[1]

  # connect python with mysql with your hostname, 
  # username, password and database
  db= MySQLdb.connect("localhost","root", "pass", "iot.eyewitness")
    
  # get cursor object
  cursor= db.cursor()

  ##############LOOK FOR CASE IN DATABASE#############
  cursor.execute("SELECT * FROM cases WHERE name = %(case_name)s",{ 'case_name': case_name }) 
  result = cursor.fetchall()
      
  if not result:
    response = input("There is no record of case " + case_name +" in the database. Do you wish to create a new case? (y/n)")
    if response == 'y': 
      add_new_case(case_name, cursor, db)
    else :
      return


  ###############IS THE FOLDER PATH VALID##############
  if not os.path.exists(folder_path):
    print("The folder_path doesn't exist.")
    return 
  

  ##########INFORMING THE USER########################
  print("The following files will be analysed:")
  
  xlsfiles = glob.glob(folder_path+"/*.xls")
  tcxfiles = glob.glob(folder_path+"/*.tcx")
  jsonfiles = glob.glob(folder_path+"/*.json")
  print("EXCEL FILES : ", xlsfiles)
  print("TCX FILES : " ,  tcxfiles)
  print("JSON FILES : ",  jsonfiles)


  cursor.execute("SELECT id FROM cases WHERE name = %(case_name)s",{ 'case_name': case_name })
  id = str(cursor.fetchone()[0])

  updateXLSfiles(xlsfiles,cursor, db,case_name,id)
  updateTCXfiles(tcxfiles,cursor, db,case_name,id)
  updateJSONfiles(jsonfiles, cursor, db, case_name, id)

  return 
 
 
  
def updateXLSfiles(xlsfiles, cursor,db,case_name,case_id):
  for i in xlsfiles:
    xls = xlrd.open_workbook(i, on_demand=True)
    print(xls.sheet_names())
    sheets = []
    for k in xls.sheet_names():
      if "Log" not in k:
        sheets.append(k)
  
    #print(sheets,"\n\n\n\n\n")

    df = pd.read_excel(i, sheet_name=sheets)
    demand_dict = {}
    for key, df in df.items():
      print(key, df)
      #print(df)
      demand_dict[key] = df

    print("--------------------------------")

    short_name = i[i.find("\\")+len("\\"):i.rfind(".")]

    for label, content in demand_dict.items():
     # print(label,content.columns)
      
      table_name = case_id + "_" + short_name + "_" + label
      table_name = table_name.replace("-","_");
      table_name = table_name.lower()
      print(table_name)
      
      #mySql_insert_query = " INSERT INTO cases(name) VALUES ('%s') "
      #return

      sql = """CREATE TABLE if not exists `%s`(""" % table_name

      print(content.columns)
      for i in content.columns:
        i=i.replace(" ","_")
        print(i)
        if i == "Date":
          sql += """ %s varchar(45) NOT NULL UNIQUE,""" % i 
        else:
          sql += """ %s varchar(45),""" % i 

      sql = sql[:-1:]
      sql += ");"
      

      print(sql )
      cursor.execute(sql)   

      print(content.columns)
     

      records = content.to_records(index=False)
      result = list(records)
      #print(result)
      
      for x in result:
        query = """INSERT IGNORE INTO `%s`(""" % table_name
        for k in content.columns:
          k=k.replace(" ","_")
          query += """ %s,""" % k 

        query = query[:-1:]
        query += ") VALUES ("

        #print(x)
        for i in x:
          query += """ '%s',""" % i

        query = query[:-1:]
        query += ");"

        print(query )

        cursor.execute(query)  
        db.commit()


def updateTCXfiles(tcxfiles, cursor,db,case_name,case_id):
  for i in tcxfiles:
    column_names = []
    #print(dir(tcxparser.TCXParser))
    for k in dir(tcxparser.TCXParser(i)):
      if not k.startswith("_"):
        column_names.append(k)

    print(column_names)

    short_name = i[i.find("\\")+len("\\"):i.rfind(".")]

    table_name = case_id + "_" + short_name + "_gps"
    table_name = table_name.replace("-","_");
    table_name = table_name.lower()
    print(table_name)

    ###########INSERTING DATA INTO CURRENT TABLE##########
    tcx = tcxparser.TCXParser(i)
    #print(">>>>>",vars(tcx))
    print(tcx)
    dict = {}
    for k in dir(tcx):
      try:
            dict[k] = getattr(tcx, k)
            print(k, getattr(tcx, k))   
      except Exception as err:
        print(k, " has no attribute")

      """ try:
        if not inspect.ismethod(getattr(tcx, k))  and not k.startswith("_"):
          if not type(getattr(tcx, k)).__name__ == "ObjectifiedElement":
            dict[k] = getattr(tcx, k)
            print(k, getattr(tcx, k))   
      except Exception as err:
        print(k, " has no attribute")
      """
    print(dict)
    sql = """CREATE TABLE if not exists `%s`(""" % table_name
    for k in dict.keys():
      k=k.replace(" ","_")
      if k == "completed_at":
          sql += """ %s varchar(45) NOT NULL UNIQUE,""" % k 
      else:
        sql += """ %s varchar(45),""" % k 

    sql = sql[:-1:]
    sql += ");"
    
    print(sql)
    cursor.execute(sql)
    
    query = """INSERT IGNORE INTO `%s`(""" % table_name
    print(len(dict.keys()))
    for key in dict.keys():
      key=key.replace(" ","_")
      query += """ %s,""" % key 
        

    query = query[:-1:]
    query += ") VALUES ("   

    for value in dict.values():
        query += """ '%s',""" % value

    query = query[:-1:]
    query += ");"

    print(query )

    cursor.execute(query)  

    db.commit()


    
def updateJSONfiles(jsonfiles, cursor,db,case_name,case_id):
  

  class TypesOfTables(enum.Enum):
    user  = 0
    heart_rate = 1
    exercise = 2
    weight = 3

  for i in jsonfiles:
    type = -1
    if "User-Profile" in i: type = TypesOfTables.user
    elif "heart_rate" in i: type = TypesOfTables.heart_rate
    elif "exercise" in i: type = TypesOfTables.exercise
    elif "weight" in i: type = TypesOfTables.weight
    
    if type != -1:
      f = open(i)
      data = json.load(f)


      short_name = i[i.find("\\")+len("\\"):i.find("-")]
      table_name = case_id + "_" + short_name + "_profile"
      table_name = table_name.replace("-","_");
      table_name = table_name.lower()
      print(table_name)

      subdicts=[]
      if type == TypesOfTables.user:
        temp = {'encodedId': data['encodedId'],
                          'gender': data['gender'],
                          'dateOfBirth': data['dateOfBirth'],
                          'height': data['height'],
                          'weight': data['weight'],
                          'fullName': data['fullName'],
                          'timezone': data['timezone'],
                          'averageDailySteps': data['averageDailySteps']
                          }
        date_time_obj = datetime.strptime(data["dateOfBirth"], '%Y-%M-%d')
        age = (date.today().year - date_time_obj.year - ((date.today().month, date.today().day) < (date_time_obj.month, date_time_obj.day)))
        temp.update
        temp['age'] = age
        subdicts.append(temp)
          
      elif type == TypesOfTables.heart_rate:
        for k in data:
          subdicts.append({'dateTime': k['dateTime'],'bpm': k['value']['bpm']})
        
      elif type == TypesOfTables.exercise:
        
        for k in data:
          temp = {'logId': k['logId'],
                  'activityName': k['activityName'],
                  'calories': k['calories'],
                  'duration': k['duration'],
                  'startTime': k['startTime']}

          if 'tcxLink' in k:
            temp['tcxLink']: k['tcxLink'] 
          else:
            temp['tcxLink']: null

          if 'steps' in k:
            temp['steps']: k['steps'] 
          else:
            temp['steps']: null

          if 'speed' in k:
            temp['speed']: k['speed'] 
          else:
            temp['speed']: null

          if 'distance' in k:
            temp['distance']: k['distance'] 
          else:
            temp['distance']: null

          subdicts.append(temp)
          

      elif type == TypesOfTables.weight:
        for k in data:
          subdicts.append({'logId': k['logId'],
                                          'weight': k['weight'],
                                          'bmi': k['bmi'],
                                          'date': k['date'],
                                          'time': k['time']
                                          })

      print(subdicts)

  
      sql = """CREATE TABLE if not exists `%s`(""" % table_name

      for key in subdicts[0]:
        key.replace(" ","_")
        if "Id" in key or "dateTime" == key:
          sql += """ %s varchar(45) NOT NULL UNIQUE,""" % key 
        else:
          sql += """ %s varchar(45),""" % key 

      sql = sql[:-1:]
      sql += ");"
  

      print(sql )
      cursor.execute(sql)   

      for i in subdicts:
        query = """INSERT IGNORE INTO `%s`(""" % table_name
        for key in i:
          key=key.replace(" ","_")
          query += """ %s,""" % key 

        query = query[:-1:]
        query += ") VALUES ("

        #print(x)
        for value in i:
          query += """ '%s',""" % i[value]

        query = query[:-1:]
        query += ");"

        print(query )

        cursor.execute(query)  
        db.commit()


  
      f.close()

      



def add_new_case(case_name,cursor, db):
  mySql_insert_query = " INSERT INTO cases(name) VALUES ('%s') "
  record = (case_name)
  try:
    cursor.execute(mySql_insert_query % record)
    db.commit()
    print("A new case was created")
  except:
    db.rollback()


class ActivitiesTable(object):
  def __init__(self, date, calories_burned, steps, distance, floors, m_sedentary, m_lightly_active, m_fairly_active, m_very_active, activity_calories):
    self.date = date
    self.calories_burned = calories_burned
    self.steps = steps
    self.distance = distance
    self.floors = floors
    self.m_sedentary = m_sedentary
    self.m_lightly_active = m_lightly_active
    self.m_fairly_active = m_fairly_active
    self.m_very_active = m_very_active
    self.activity_calories = activity_calories
 

@dataclasses.dataclass
class Arguments:
  case_name: str
  folder_path: str


def validate(args: List[str]):
  try:
      arguments = Arguments(*args)
  except TypeError:
      raise SystemExit(USAGE)


def main() -> None:
  args = sys.argv[1:]
  if not args:
      raise SystemExit(USAGE)

  if args[0] == "--help":
      print(USAGE)
      return 
  else:
      validate(args)
  Main(args)

  

if __name__=="__main__":
  main()





