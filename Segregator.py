# Segregate the Files in according to the File Content

import os
import shutil as sh
import pandas as pd
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import csv

# Define the database connection
current_directory = os.getcwd()
db_dir = os.path.join(current_directory,"./Database/data.db")
con_db = f"sqlite:///{db_dir}"
engine = create_engine(con_db)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base() # Define the base model
            
class Components(Base): 
    __tablename__ = 'Components'

    ApplicationId = Column(Integer, primary_key=True,autoincrement=True)
    MemberId = Column(Integer)
    MemberType = Column(String)
    MemberName = Column(String)
    MemberPath = Column(String)
    DB2 = Column(Boolean)
    CICS = Column(Boolean)
    IMS = Column(Boolean)
    IDMS = Column(Boolean)


def checkAreaACondition(line,word):# Checks for Area A in Fixed Format Cobol File

    if isNonComment(line):
        areaA = line.find(word)
        if areaA in range(7,11):
            return True
    return False


def checkAreaBcondition(line,word):# Checks for Area B in Fixed Format Cobol File
    if isNonComment(line):
        areaB = line.find(word)
        if areaB in range(11,72):
            return True
    return False
    
def isCOBOL(lines):
    Cobol_Constraints = False
    Cobol_DB2_Constraints = False
    Cobol_IMS_Constraints = False
    Cobol_CSIS_Contraints = False

    for line in lines:
        if isNonComment(line):
            # line.upper()
            if checkAreaACondition(line.upper(),"IDENTIFICATION DIVISION"):
                Cobol_Constraints = True
                continue
            if Cobol_Constraints:
                if isCOBOL_DB2(line):
                    Cobol_DB2_Constraints = True
                    continue
                if isCOBOL_IMS(line):
                    Cobol_IMS_Constraints = True
                    continue
                if isCICS_COBOL(line):
                    Cobol_CSIS_Contraints = True
                    continue

    if Cobol_CSIS_Contraints and Cobol_DB2_Constraints:
        return "CICS-COBOL-DB2"
    elif Cobol_CSIS_Contraints and Cobol_IMS_Constraints:
        return "CICS-COBOL-IMS"
    elif Cobol_DB2_Constraints:
        return "COBOL-DB2"
    elif Cobol_IMS_Constraints:
        return "COBOL-IMS"
    elif Cobol_CSIS_Contraints:
        return "CICS-COBOL"
    elif Cobol_Constraints:
        return "COBOL"
    else:
        return None
    

def isJCL(lines): #Checks for JCL constraints
    for line in lines:
        if "*" in line:
            continue
        elif (line.startswith("//") and "JOB" in line and isNonComment(line)):
            return "JCL"
    return None

def isNonComment(line): # Checks for Executable Lines and skipping the Empty lines as Well
    empty  = line.strip() ==""   
    if empty or "*" in line:
        return False
    return True


def isCOBOL_DB2(line): #check for Possibility of being a COBOL-DB2 file
    if isNonComment(line) :
        if checkAreaBcondition(line,"EXEC SQL"):
            return True
    return False

def isCOBOL_IMS(line):#check for Possibility of being a COBOL-IMS file
    if isNonComment(line):
        if checkAreaBcondition(line,"CALL 'CBLTDLI'"):
            return True
    return False

def isCICS_COBOL(line):#check for Possibility of being a COBOL-CSIC file
    if isNonComment(line) :
        if checkAreaBcondition(line,"EXEC CICS"):
            return True
    return False
 

def is_JCL_PROC(lines): #check for JCL PROCEDURE file 
    for line in lines:
        if not isNonComment(line):
            continue
        elif (line.startswith("//") and "PROC" in line):
            return "JCL_PROC"
    return None


def isREXX(lines): # check for Rexx File
    for line in lines:
        if line.startswith("/*") and "REXX" in line:
              return "REXX"
    return None



# 
# 

Mapper = {
    "JCL": isJCL,
    "JCL_PROC": is_JCL_PROC,
    "COBOL": isCOBOL,
    "REXX": isREXX,
}

# IF Futher rules that can be added into mapper

# "CLIST":"isCLIST",
# "ASSEMBLER":"isASSEMBLER",
# "PL1":"isPL1"

def inspectFile(lines, Mapper):
    for Folder, Method in Mapper.items():

        file_type = Method(lines)
        if file_type is None:
            # print("UNDEF")
            continue
        # print(file_type)
        return file_type
    return None


def getListOfFiles(dirName):
    # create a list of file and sub directories
    listOfFile = os.listdir(dirName)
    allFiles = list()    

    for entry in listOfFile: #Iterate over all the entries
        fullPath = os.path.join(dirName, entry)# Create full path
        if os.path.isdir(fullPath): # If entry is a directory then get the list of files in this directory
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            head,filename=os.path.split(fullPath)
            allFiles.append(fullPath)               
    return allFiles

def segregate_files(ip_dir,op_dir):
    index =1
    set_batch_files = getListOfFiles(ip_dir)
    for file in set_batch_files:
        with open(file,"r") as f:
            lines = f.readlines()
            file_type = inspectFile(lines,Mapper) #Interpret the File             
            
            data_handling(index,file,file_type) # Extending Functionality to inserting the Data into Model based Table
            index +=1

            if file_type is not None:
                output_subfolder = os.path.join(op_dir, file_type)
                os.makedirs(output_subfolder, exist_ok=True)
                if os.path.exists(output_subfolder):
                    sh.copy(file, output_subfolder)
                else:
                    sh.move(file, output_subfolder)
                continue
            else:
                output_subfolder = os.path.join(op_dir, "UNDEFINED")
                os.makedirs(output_subfolder, exist_ok=True)
                if os.path.exists(output_subfolder):
                    sh.copy(file, output_subfolder)
                else:
                    sh.move(file, output_subfolder)

    data_Transformer(op_dir)
    filter = {"MemberType":"COBOL"}
    # data_Transformer_Filter(op_dir)
    print("Segregation Successful")




def data_handling(id,file,file_type):
    if file_type is None :
        file_type = "UNDEF"
    file_name = file_name = os.path.basename(file)
    isDB2 = False 
    isCICS = False
    isIMS = False
    isIDMS = False
    if "DB2" in file_type:
        isDB2 = True
    if "CICS" in file_type:
        isCICS = True
    if "IMS" in file_type:
        isIMS = True
    if "IDMS" in file_type:
        isIDMS = True

    Query = insert(Components).values(MemberId = id,MemberType = file_type,MemberName = file_name,MemberPath = file,DB2 = isDB2,CICS = isCICS,IMS = isIMS,IDMS = isIDMS)
    session.execute(Query)
    session.commit()
    return None


def data_Transformer(opdir):
    # Write python scripts to query on the inventory tables to take dynamic parameters for filtering and generate the reports in CSV
    query = session.query(Components).all()
    df = pd.DataFrame([(c.ApplicationId, c.MemberId, c.MemberType, c.MemberName, c.MemberPath, c.DB2, c.CICS, c.IMS, c.IDMS)
                    for c in query],
                    columns=['ApplicationId', 'MemberId', 'MemberType', 'MemberName', 'MemberPath',
                            'DB2', 'CICS', 'IMS', 'IDMS'])
    dir = os.path.dirname(opdir)
    output_file = os.path.join(dir,"./Data_Models/Component.xlsx")
    df.to_excel(output_file, index=False)

    print("Data exported to Excel successfully.")

    return None

def data_Transformer_Filter(opdir,filter,option):
    
    if isinstance(filter,str):
        file = filter["type"]
        query = session.query(Components).filter(Components.MemberType == filter["type"],Components.DB2 == False)
        df = pd.DataFrame([(c.ApplicationId, c.MemberId, c.MemberType, c.MemberName, c.MemberPath, c.DB2, c.CICS, c.IMS, c.IDMS)
                        for c in query],
                        columns=['ApplicationId', 'MemberId', 'MemberType', 'MemberName', 'MemberPath',
                                'DB2', 'CICS', 'IMS', 'IDMS'])
        dir = os.path.dirname(opdir)
        output_file = os.path.join(dir,f"./Data_Models/{file}_Folder.xlsx")
        
        df.to_excel(output_file, index=False)
        print(f"Report generated successfully: {output_file}")
    if isinstance(filter,dict):
        # option = str(input("Want To Tranform the Data Specified by Filter into a Single File?(YES/NO)"))
        li = filter["type"]
        if option =="YES":
            file__n = "Filtered_Membered_Components"
            filtered_data = pd.DataFrame(columns=['ApplicationId', 'MemberId', 'MemberType', 'MemberName', 'MemberPath',
                                'DB2', 'CICS', 'IMS', 'IDMS'])
            for item in li:
                query = session.query(Components).filter(Components.MemberType == item)
                df = pd.DataFrame([(c.ApplicationId, c.MemberId, c.MemberType, c.MemberName, c.MemberPath, c.DB2, c.CICS, c.IMS, c.IDMS)
                            for c in query],
                            columns=['ApplicationId', 'MemberId', 'MemberType', 'MemberName', 'MemberPath',
                                    'DB2', 'CICS', 'IMS', 'IDMS'])
                filtered_data=filtered_data.append(df)
                
            
            dir = os.path.dirname(opdir)
            output_file = os.path.join(dir,f"./Data_Models/{file__n}_Folder.xlsx")        
            filtered_data.to_excel(output_file, index=False)
            print(f"Report generated successfully: {file__n}")
        else:
            for item in li:
                query = session.query(Components).filter(Components.MemberType == item)
                df = pd.DataFrame([(c.ApplicationId, c.MemberId, c.MemberType, c.MemberName, c.MemberPath, c.DB2, c.CICS, c.IMS, c.IDMS)
                            for c in query],
                            columns=['ApplicationId', 'MemberId', 'MemberType', 'MemberName', 'MemberPath',
                                    'DB2', 'CICS', 'IMS', 'IDMS'])
                dir = os.path.dirname(opdir)
                output_file = os.path.join(dir,f"./Data_Models/{item}_Folder.xlsx")        
                df.to_excel(output_file, index=False)
                print(f"Report generated successfully: {item}")

    return None



if __name__ == "__main__": 

    parent_dir= os.path.abspath(__file__)
    input_directory  = os.path.join(os.path.dirname(parent_dir),"Resources/Input_Directory")
    output_directory = os.path.join(os.path.dirname(parent_dir),"Resources/Output_Directory")

    segregate_files(input_directory,output_directory)
    filter = {
        "type" :["COBOL","JCL","CICS-COBOL-DB2","COBOL-DB2"]
    }
    data_Transformer_Filter(output_directory,filter,"YES")
    
