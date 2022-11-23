import datetime
import json
import os
import re
import typing as tp

import matplotlib.pyplot as plt
import numpy as np
import requests
from requests.adapters import HTTPAdapter, Retry

import pandas as pd
import streamlit as st

NGINX_URL = os.getenv("NGINX_URL")
assert NGINX_URL is not None

UI_TO_MIDDLEWARE_URL = f"{NGINX_URL}/"
UI_TO_REPORT_STORAGE_URL = f"{NGINX_URL}/reports"


NUM_TO_MONTH = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def extract_datetime(datetime_str: str) -> datetime.datetime:
    for i, month in enumerate(NUM_TO_MONTH):
        month_num = f"{i:02d}"
        datetime_str = datetime_str.replace(month, month_num)
    return datetime.datetime.strptime(datetime_str, "%d-%m-%Y %H:%M")


def init_session() -> requests.Session:
    s = requests.Session()

    fail_codes_html = [500, 502, 503, 504]

    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=fail_codes_html)
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount(f"http://", HTTPAdapter(max_retries=retries))

    report_retries = Retry(total=5, backoff_factor=1, status_forcelist=[404] + fail_codes_html)
    s.mount(f"{NGINX_URL}/reports/", HTTPAdapter(max_retries=report_retries))

    return s


def demand_report(session: requests.Session, dataset_name: str) -> tp.Optional[str]:
    get_cur_report_url = UI_TO_MIDDLEWARE_URL + f"report?test_group_id={dataset_name}"
    r = session.get(get_cur_report_url)
    if r.status_code != 200:
        return None
    report_url = r.content.decode()[1:-1]
    report_name = report_url.split("/")[-1]
    return report_name


def get_report_by_name(session: requests.Session, report_name: str) -> tp.Optional[pd.DataFrame]:
    cur_report_url = f"{UI_TO_REPORT_STORAGE_URL}/{report_name}"
    r = session.get(cur_report_url)
    if r.status_code != 200:
        return None
    report_data = json.loads(r.content.decode())
    report_data = {k: [v] for k, v in report_data.items()}
    return pd.DataFrame(report_data, index=[report_name])


def get_recent_report_names(session: requests.Session, top_k: int = 3) -> tp.Optional[tp.List[str]]:
    r = session.get(f"{UI_TO_REPORT_STORAGE_URL}/")
    if r.status_code != 200:
        return None
    files_table = r.content.decode()
    datetime_pattern = re.compile("\d\d-\w\w\w-\d\d\d\d \d\d:\d\d")
    dates = re.findall(datetime_pattern, files_table)
    dates = map(extract_datetime, dates)
    dates = list(map(lambda x: x.timestamp(), dates))
    recent_timestamp_ids = np.argsort(dates)[-top_k:]

    report_pattern = ">\w*.json<"
    report_links = re.findall(report_pattern, files_table)
    report_links = list(map(lambda x: x[1:-1], report_links))
    recent_reports = [report_links[i] for i in recent_timestamp_ids]
    return recent_reports


def get_report_st(dataset_name, session):
    st.header(f"Report for dataset \"{dataset_name}\":")
    report_name = demand_report(session, dataset_name)
    if report_name is not None:
        df = get_report_by_name(session, report_name)
        if df is not None:
            st.write(df)


def get_recent_reports_st(session):
    st.header("Recent reports summary:")
    report_names = get_recent_report_names(session)
    dfs = []
    for report_name in report_names:
        cur_df = get_report_by_name(session, report_name)
        if cur_df is not None:
            dfs.append(cur_df)
    if len(dfs) > 0:
        df = pd.concat(dfs)
        st.write(df)
        df = df.reset_index()
        df["index"] = df["index"].apply(lambda x: "_".join(map(lambda x: x[:4] + "...", x.split("_"))))
        df = df.rename(columns={"index": "report name"})

        fig, axs = plt.subplots(1, 3, figsize=(12, 6))
        for ax, name in zip(axs, ["total_samples", "n_classes", "accuracy"]):
            ylim = None
            if name == "accuracy":
                ylim = (0, 1)
            df.plot(x="report name", y=name, ax=ax, kind="bar", ylim=ylim, legend=False, title=name)
            ax.grid(visible=True, axis="y")

        st.pyplot(fig)


def main() -> None:
    session = init_session()

    st.header("Reports")
    dataset_name = st.text_input("Dataset name")

    if st.button("Get report for the dataset"):
        get_report_st(dataset_name, session)
        get_recent_reports_st(session)

    if st.button("Compare last 3 reports"):
        get_recent_reports_st(session)


if __name__ == "__main__":
    main()
