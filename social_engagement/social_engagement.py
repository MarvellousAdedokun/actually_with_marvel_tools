import pandas as pd
import matplotlib.pyplot as plt

CSV_PATH = "social_posts.csv"
ORANGE = "#E8630A"
BLACK = "#0A0A0A"
WHITE = "#FFFFFF"
GREY = "#999999"

def load_data(csv_path):
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df['date'])
    df['engagements'] = df['likes'] + df['comments']
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

def engagement_by_type_chart(df, out_path = "chart_engagement_by_type.png"):
    avg_by_type = df.groupby("post_type")["engagement"].mean().sort_values()

    fig, ax = plt.subplots(figsize=(10, 7), facecolor=BLACK)
    ax.set_facecolor(BLACK)
    ax.barh(avg_by_type.index, avg_by_type.values, color=ORANGE)
    ax.set_title("Average engagement by post type", color=WHITE, fontsize=18, pad=20, loc="left")
    ax.tick_params(colors=GREY, labelsize=12)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#333333")
    for i, v in enumerate(avg_by_type.values):
        ax.text(v + 1, i, f"{v:.0f}", color=WHITE, va="center", fontsize=12)

    plt.tight_layout()
    plt.savefig(out_path, facecolor=BLACK, dpi=200)
    plt.close()
    print(f"Saved {out_path}")


if __name__ == "__main__":
    df = load_data(CSV_PATH)

    print("=== POSTING FREQUENCY ===")
    print(posting_frequency(df))

    print("\n=== ENGAGEMENT STATS ===")
    engagement_stats(df)

    engagement_trend_chart(df)
    engagement_by_type_chart(df)
