import pymysql.cursors

print(pymysql.connect(host='192.168.2.171',
                                     user='Hubo',
                                     password='Hubo2015',
                                     database="videos",
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor))