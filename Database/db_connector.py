import mysql.connector

def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="osintRoot@786",
        database="aws_cloud2"
    )



# def connect_to_database():
#     return mysql.connector.connect(
#         host="cloudstorage1.mysql.database.azure.com",  # Your Azure MySQL server name
#         user="pakistan123@cloudstorage1",  # Your Azure MySQL server admin login name
#         password="root@1981",  # Your Azure MySQL password
#         database="aws_cloud"  # Your database name
#     )
