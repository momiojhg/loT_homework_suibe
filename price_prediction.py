import pandas as pd
import sqlite3
from sqlite3 import Error
from sklearn.linear_model import LinearRegression

class GoldFuturesModel:
    def __init__(self):
        self.db_file = "maotai_futures.db"  # 数据库文件名
        self.conn = self.create_connection()

    def create_connection(self):
        """创建数据库连接"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            print(f"成功连接到SQLite数据库: {self.db_file}")
        except Error as e:
            print(f"连接数据库时出错: {e}")
        return conn

    def get_all_data(self):
        """从数据库获取所有数据"""
        select_sql = "SELECT * FROM gold_futures"
        try:
            df = pd.read_sql_query(select_sql, self.conn)
            return df
        except Error as e:
            print(f"从数据库获取数据时出错: {e}")
            return None

    def train_and_predict(self):
        """训练模型并进行预测"""
        data = self.get_all_data()
        if data is not None and not data.empty:
            # 选取特征和目标变量
            X = data[['latest_price', 'open_price', 'high_price', 'low_price', 'volume']]
            y = data['latest_price'].shift(-1).dropna()
            X = X[:-1]

            # 训练线性回归模型
            model = LinearRegression()
            model.fit(X, y)

            # 获取最新数据进行预测
            latest_data = self.get_latest_data(1)[0]
            latest_features = [latest_data['latest_price'], latest_data['open_price'], latest_data['high_price'], latest_data['low_price'], latest_data['volume']]
            prediction = model.predict([latest_features])
            return prediction[0]
        return None

    def get_latest_data(self, limit=5):
        """从数据库获取最新的几条数据"""
        select_sql = f"""
        SELECT * FROM gold_futures 
        ORDER BY update_time DESC 
        LIMIT {limit}
        """

        try:
            cursor = self.conn.cursor()
            cursor.execute(select_sql)
            rows = cursor.fetchall()

            # 获取列名
            columns = [description[0] for description in cursor.description]

            # 将结果转换为字典列表
            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))

            return results
        except Error as e:
            print(f"从数据库获取数据时出错: {e}")
            return None


if __name__ == "__main__":
    model = GoldFuturesModel()
    prediction = model.train_and_predict()
    if prediction is not None:
        print(f"茅台下一个时刻的预测价格: {prediction}")
    else:
        print("未能进行有效预测")

    model.conn.close()