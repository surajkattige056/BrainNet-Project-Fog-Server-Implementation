import pyedflib
import re
import numpy as np
import sqlite3
from sqlite3 import Error
import flask as g
from flask import Flask
from flask import request
from sklearn import svm
import os

clf = svm.SVC()

def edf_parser(file):
    try:
        f = pyedflib.EdfReader(file)
        n = f.signals_in_file
        patient = f.patientname
        signal_labels = f.getSignalLabels()
        sigbufs = np.zeros((n, f.getNSamples()[0]))
        for i in np.arange(n):
            sigbufs[i, :] = f.readSignal(i)
        return sigbufs, patient
    except Exception as ex:
        print ex

app = Flask(__name__)
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None

def select_distinct_user(conn):
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT User FROM PatientData")
    rows = cur.fetchall()
    return rows

def select_user(conn, user):
    cur = conn.cursor()
    cur.execute("SELECT EDF FROM PatientData WHERE User = ?", user)
    rows = cur.fetchall()
    return rows



def insert_reading(conn, user_data):
    cur = conn.cursor()
    sql = '''INSERT INTO PatientData(User , ID, EDF)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql,user_data)
    return cur.lastrowid



def database_query(patient):
    value = False
    database = 'brainnetdata2.db'
    conn_db = create_connection(database)
    user_file = select_user(conn_db, patient)
    if (len(user_file) > 0):
        value = True
    return user_file, value


def generate_trainDictionary():
    database = 'brainnetdata.db'
    conn_db = create_connection(database)
    distinct_users = select_distinct_user(conn_db)
    for i in range(len(distinct_users)):
        distinct_users[i] = distinct_users[i][0]
    X = []
    y = []
    for i in range(len(distinct_users)):
        user_data = generate_trainData(conn_db,distinct_users[i])
        for l in range(len(user_data)):
            for k in range(len(user_data[l])):
                temp = np.zeros((20000), dtype=np.complex128)
                for j in range(len(user_data[l][k])):
                    temp[j] = user_data[l][k][j]
                X.append(temp)
                y.append(distinct_users[i])
    # print distinct_users
    training_data(X, y)

def generate_trainData(conn, user):
    user_data = []
    edf_files = select_user(conn, user)
    for i in range(len(edf_files)):
        user_signal, patient = edf_parser(filename(edf_files[i]))
        user_data.append(user_signal)
    return user_data

def training_data(X, y):
    (clf.fit(X,y))

def filename(user_file):
    user_filename = user_file[0]
    user_filename = re.findall(".*/(.*.edf)", user_filename)
    user_filename = user_filename[0].decode('UTF-8')
    return user_filename

def comparator(signal):
    users = dict()
    real_signal = []
    for i in range(len(signal)):
        temp = np.zeros((20000), dtype=np.complex128)
        for j in range(len(signal[i])):
            temp[j] = signal[i][j]
        real_signal.append(temp)

    user = clf.predict(real_signal)
    for i in user:
        if users.__contains__(i):
            users.__setitem__(i, users[i] + 1)
        else:
            users[i] = 1
    return users

def accuracy(users, patient):
    total = 0
    if users.__contains__(patient):
        for key in users.keys():
            total += users[key]
        accuracy = (users[patient]/total)* 100
    else:
        accuracy = 0
    return accuracy

@app.route('/', methods = ['POST'])
def main():
    output = "0"
    data = request.get_data()
    pos = data.find("\r\n\r\n")
    # print pos
    data = data[pos + 4:]
    f = open('test1.edf', 'wb')
    f.write(data)

    f.close()
    signal, patient = edf_parser('test1.edf')
    user_file, exists = database_query(patient)
    if exists:
        output = comparator(signal)
        hits = accuracy(output, patient)
        print "The accuracy is: ",hits,"%"
        print("Sending: ")
        if hits > 70:
            output = "1"
        else:
            output = "0"
    else:
        output = 0

    print "Sending value: ", output
    return output


if __name__ == '__main__':
    generate_trainDictionary()
    app.run('0.0.0.0', 50000)




