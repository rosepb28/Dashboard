import argparse
import datetime
import subprocess

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--daily", action="store_true", help="Generate daily report")
parser.add_argument("--monthly", action="store_true", help="Generate monthly report")
args = parser.parse_args()

# Check if the daily report should be generated
if args.daily:
    subprocess.run(["python", "src/daily_report.py"])


# Check if the monthly report should be generated
if args.monthly and datetime.datetime.now().day != 1:
    subprocess.run(["python", "src/monthly_report.py"])
