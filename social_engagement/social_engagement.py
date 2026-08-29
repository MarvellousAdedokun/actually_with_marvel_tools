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

def engagement_stats(df):
    """
    Average engagement overall, and broken down by post type.
    """
    df["engagement"].mean()
    df.groupby("post_type")["engagement"]

    pass

def engagement_trend_chart(df, out_path="chart_engagement_trend.png"):
    df_sorted = df.sort_values("date")
    fig, ax = plt.subplots(figsize=(10, 7), facecolor=BLACK)
    ax.set_facecolor(BLACK)
    ax.plot(df_sorted['date'], df_sorted['engagement'], color = ORANGE, marker = "o")
    ax.set_title("Engagement over time", color=WHITE, fontsize=18, pad=20, loc="left")
    ax.tick_params(colors=GREY)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#333333")

    plt.tight_layout()
    plt.savefig(out_path, facecolor=BLACK, dpi=200)
    plt.close()
    print(f"Saved {out_path}")

        
        



