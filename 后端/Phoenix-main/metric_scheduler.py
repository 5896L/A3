import threading

from dm_constants import dm_metrics

class MetricScheduler:
    def __init__(self, db):
        self.db = db

    def query_metric(self, metric):
        if metric in dm_metrics:
            query = dm_metrics[metric]
            results = self.db.execute_query(query)
            if results:
                print(f"{metric}: {results[0][0]}")
            else:
                print(f"No results found for {metric}")
        else:
            print(f"Metric {metric} not found")

    def schedule_query(self, metric, interval):
        self.query_metric(metric)
        threading.Timer(interval, self.schedule_query, args=[metric, interval]).start()