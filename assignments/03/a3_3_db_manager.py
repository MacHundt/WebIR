#A3_3 solution
__author__ = 'Bassil Khatib and Michael Hundt'

import pymysql
import datetime


def main():

    generate_test_data(10)
    connection = connect_to_db()
    store_to_db(connection.cursor(), "pages", *get_values())
    connection.commit()

    #read_first_record(connection.cursor())

    db_content = read_db(connection.cursor())
    for record in db_content:
        print(record)

    connection.close()

def generate_test_data(records=100):
    fp = open("test_data.txt",mode="w")
    #wirte header
    fp.write("title;;url;;content;;creation_date\n")
    for i in range(records):
        dummy = 'Test{0};;http://www.test/url/;;Yam yam .. text to be stored!\n'.format(i)
        fp.write(dummy)
    fp.close()

def read_first_record(cursor):
    '''
    Get the first record to retrieve the field names
    :param cursor:
    :return: first record
    '''
    # Read a single record
    sql = "SELECT * FROM pages LIMIT 1"
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def read_db(cursor):
    '''
    Read the whole db
    :param cursor:
    :return: content of whole DB
    '''
    sql = "SELECT * FROM pages"
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def get_values():
    '''
    Reads in values from a simple test data file
    :return: a list of values
    '''
    ts = datetime.datetime.utcnow()
    #print(ts)
    fp = open("test_data.txt")
    header = fp.readline()
    values = list()

    for line in fp.readlines():
        value = line.rstrip().split(';;')
        value.append(str(ts))
        values.append(value)

    return values

def store_to_db(cursor, table_name, *values):
    '''
    stores the values in the table <table_name>
    :param cursor:
    :param table_name:
    :param values:
    :return: void
    '''
    #TODO get the field names to make it more generic ... they are in a different order #see get_first_record()
    # Create a new record
    sql = "INSERT INTO "+str(table_name)+"(title, url, content, creation_date ) VALUES (%s, %s, %s, %s)"
    i = 0
    for val in values:
        cursor.execute(sql, (val[0], val[1], val[2], val[3]))
        i += 1
    if i == 1:
        print("...inserted one record to db")
    else:
        print("...inserted "+str(i)+" records to db")


def connect_to_db():
    '''
    Connects to the local MySQL database
    :return: a db connection
    '''
    # Connect to the database
    try:
        connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root',   #don't know how to change the pw
                             db='scraping',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
        print("...connected to mysql db")
    except Exception as e:
        print("Connection Error")
        print(e.args[1])

    return connection


if __name__ == '__main__':
    main()