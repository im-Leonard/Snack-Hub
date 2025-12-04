import mysql.connector
from mysql.connector import pooling
from config import DB_CONFIG

pool = pooling.MySQLConnectionPool(
    pool_name="snackhub_pool",
    pool_size=10,
    **DB_CONFIG
)

def get_conn():
    return pool.get_connection()
