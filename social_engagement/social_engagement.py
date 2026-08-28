import pandas as pd
import matplotlib.pyplot as plt

CSV_PATH = "social_posts.csv"
ORANGE = "#E8630A"
BLACK = "#0A0A0A"
WHITE = "#FFFFFF"
GREY = "#999999"

def load_data(csv_path):
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df['dates'])
    df['engagements'] = df['likes'] + df['date']
    return df

def posting_frequency(df):
    """
    How many posts per week/month — is posting consistent or sporadic?
    """
    post_per_week = df.groupby(pd.Grouper(key="date", freq="W")).size()
    post_per_month = df.groupby(pd.Grouper(key="date", freq="M")).size()

    return post_per_month, post_per_week


