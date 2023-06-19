import psutil
import time
from pymongo import MongoClient
import matplotlib.pyplot as plt

class Power:
    MONGODB_CONNECTION_STRING = 'mongodb://localhost:27017/'

    def __init__(self):
        self.cpu_percent = None
        self.ram_total = None
        self.ram_used = None
        self.timestamp = None

    def update_stats(self):
        self.cpu_percent = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        self.ram_total = mem.total
        self.ram_used = mem.used
        self.timestamp = time.time()

    def save_to_database(self):
        client = MongoClient(self.MONGODB_CONNECTION_STRING)
        db = client['power_stats']
        collection = db['logs']
        log = {
            'cpu_percent': self.cpu_percent,
            'ram_total': self.ram_total,
            'ram_used': self.ram_used,
            'timestamp': self.timestamp
        }
        collection.insert_one(log)
        client.close()

    @staticmethod
    def delete_old_logs():
        client = MongoClient(Power.MONGODB_CONNECTION_STRING)
        db = client['power_stats']
        collection = db['logs']
        count = collection.count_documents({})
        if count > 10000:
            oldest_logs = collection.find().sort('timestamp', 1).limit(count - 10000)
            for log in oldest_logs:
                collection.delete_one({'_id': log['_id']})
        client.close()

    @staticmethod
    def plot_graph():
        client = MongoClient(Power.MONGODB_CONNECTION_STRING)
        db = client['power_stats']
        collection = db['logs']
        data = collection.find()

        timestamps = []
        cpu_percent = []
        ram_total = []
        ram_used = []

        for log in data:
            timestamps.append(log['timestamp'])
            cpu_percent.append(log['cpu_percent'])
            ram_total.append(log['ram_total'])
            ram_used.append(log['ram_used'])

        client.close()

        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, cpu_percent, label='CPU %')
        plt.plot(timestamps, ram_total, label='RAM Total')
        plt.plot(timestamps, ram_used, label='RAM Used')
        plt.xlabel('Timestamp')
        plt.ylabel('Percentage / Bytes')
        plt.title('Power Statistics')
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == '__main__':
    power = Power()

    while True:
        power.update_stats()
        power.save_to_database()
        power.delete_old_logs()
        time.sleep(1)  # Wait for 1 second before updating again