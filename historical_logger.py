import os
import csv
from datetime import datetime

HIST_DIR = 'historical-data'

os.makedirs(HIST_DIR, exist_ok=True)


def log_packet_csv(data_type: str, headers: list, values: list):
    """Append a row to a CSV file named by data_type under historical-data/.

    - data_type: filename base (e.g. 'AHT20', 'SEN0169')
    - headers: list of column names (excluding date_received)
    - values: list of values matching headers order

    The function will create the file and write a header row if it doesn't exist.
    """
    # sanitize filename
    filename = f"{data_type}.csv"
    path = os.path.join(HIST_DIR, filename)

    write_header = not os.path.exists(path) or os.path.getsize(path) == 0

    # Ensure values are converted to basic types
    row = [datetime.now().astimezone().isoformat()] + [v for v in values]

    with open(path, 'a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['date_received'] + headers)
        writer.writerow(row)
