from datetime import datetime
from typing import Dict, Final, Optional, Tuple

import time
import os
import subprocess

import dotenv
import requests

dotenv.load_dotenv(".env")

AUTH: Optional[str] = os.environ.get("AUTH")

assert AUTH is not None
assert AUTH.isascii()

CURRENT_YEAR = datetime.now().year
YEAR: Final[str] = os.environ.get("YEAR") or str(CURRENT_YEAR - 1)

URL: Final[str] = f"http://localhost:42001/epitest/me/{YEAR}/"


def _format_cs_report(results):
    reports = []

    for item in results["externalItems"]:
        if not item["type"].startswith("lint"):
            continue

        if item["value"] == 0.0:
            continue

        _, _, name = item["type"].partition(".")

        value = int(item["value"])
        reports.append(f"{value} {name}")

    return ', '.join(reports) or "No reports"


def print_skill_report(results):
    skills: Dict[str, Dict[str, int]] = results["skills"]
    pad = len(max(skills.keys(), key=len)) + 1

    total_count = 0
    total_passed = 0

    def _retrieve_metrics(metrics) -> Tuple[int, int, int]:
        return (
            metrics["count"],
            metrics["passed"],
            metrics["crashed"]
        )

    for section_name, metrics in skills.items():
        count, passed, crashed = _retrieve_metrics(metrics)
        prog = (passed / count) * 100

        print(f"{section_name:<{pad}}  {passed} / {count}  {prog:.1f}%")

        if crashed:
            print("-!>", crashed, "crash detected !")

        total_count += count
        total_passed += passed

    prog = (total_passed / total_count) * 100

    print(end='\n')
    print(f"{'Total':<{pad}}  {total_passed} / {total_count}  {prog:.1f}%")



def pretty_print(data):
    date: datetime = datetime.strptime(data["date"], "%Y-%m-%dT%H:%M:%SZ")
    results = data["results"]
    
    print("Last Report from", date)
    print("Project", data["project"]["name"])
    print(end='\n')

    if results["mandatoryFailed"] == 1:
        print("Warning: Mandatory Failed Detected!")

    print("Coding Style:", _format_cs_report(results))
    print(end="\n")

    print("-- Results --")
    print_skill_report(results)


def ping_api(headers):
    try:
        response = requests.get(URL, headers=headers)
        return response.ok
    except (
        requests.exceptions.ConnectTimeout,
        requests.exceptions.ConnectionError
    ):
        return False


def wait_for_api(headers):
    while not ping_api(headers):
        time.sleep(2)


def main():
    _headers = { "Authorization": AUTH }
    if not ping_api(_headers):
        subprocess.Popen(["my-epitech-relay"], shell=True)

    wait_for_api(_headers)

    response = requests.get(URL, headers=_headers)
    if not response.ok:
        print("Failed to request the url:", response.status_code)
        return

    try:
        json = response.json()

    except requests.JSONDecodeError:
        print("Error while trying to decode the json respone.")
        return

    last_entry = max(json, key=lambda d: d["date"])
    pretty_print(last_entry)
    time.sleep(1)


if __name__ == "__main__":
    main()
