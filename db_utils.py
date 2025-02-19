import mysql.connector
from mysql.connector import Error

db_config = {
    'user': 'root',
    'password': '*******',  # 替换为您的密码
    'host': '192.168.4.56',
    'database': 'xs_ocr_ret',
    'raise_on_warnings': True
}

def connect_to_db():
    """Connects to the MySQL database."""
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print('Connected to MySQL database')
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def insert_ocr_data(img_name, url, crop_box, ocr_text):
    """Inserts OCR data into the database."""
    connection = connect_to_db()
    if connection is None:
        return False
    
    # 创建游标对象
    cursor = connection.cursor()
    try:
        sql = """
        INSERT INTO my_test (img_name, url, crop_box, ocr_text)
        VALUES (%s, %s, %s, %s)
        """
        values = (img_name, url, str(crop_box), ocr_text)
        # 执行插入操作
        cursor.execute(sql, values)
        # 提交事务
        connection.commit()
        print("Data inserted successfully")
        return True
    except Error as e:
        print(f"Error inserting data: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
