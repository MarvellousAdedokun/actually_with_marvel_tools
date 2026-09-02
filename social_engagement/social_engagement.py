import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = BASE_DIR / "social_posts.csv"
ORANGE = "#E8630A"
BLACK = "#0A0A0A"
WHITE = "#FFFFFF"
GREY = "#999999"

# Consistent slide-deck-ready sizing
FIGSIZE = (12, 7)
TITLE_SIZE = 22
LABEL_SIZE = 14
TICK_SIZE = 13
DPI = 300  # print/projector quality, not just screen quality


def load_data(csv_path):
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df['date'])
    df['engagements'] = df['likes'] + df['comments'] + df['shares'] + df['saves']
    return df


def posting_frequency(df):
    """
    How many posts per week/month — is posting consistent or sporadic?
    """
    post_per_week = df.groupby(pd.Grouper(key="date", freq="W")).size()
    post_per_month = df.groupby(pd.Grouper(key="date", freq="ME")).size()

    return post_per_month, post_per_week


def engagement_stats(df):
    """
    Average engagement overall, and broken down by post type.
    """
    overall_avg = df["engagements"].mean()
    by_type_avg = df.groupby("post_type")['engagements'].mean().sort_values(ascending=False)
    return overall_avg, by_type_avg


def best_worst_posts(df):
    """
    Identify the single best- and worst-performing post by engagement.
    This is the concrete, specific detail a generic Insights dashboard
    average can't hand someone — a real post, a real date, a real number.
    """
    best = df.loc[df["engagements"].idxmax()]
    worst = df.loc[df["engagements"].idxmin()]
    return best, worst


def generate_recommendation(by_type_avg, best_post):
    """
    Turn the numbers into a single, plain-language decision.
    This is the line that separates 'here are your stats' from 'here's what to do'.
    """
    top_type = by_type_avg.index[0]
    top_avg = by_type_avg.iloc[0]
    lowest_type = by_type_avg.index[-1]
    lowest_avg = by_type_avg.iloc[-1]

    if lowest_avg > 0:
        multiplier = top_avg / lowest_avg
    else:
        multiplier = float("inf")

    recommendation = (
        f"Post more {top_type}s, fewer {lowest_type}s — {top_type}s are earning "
        f"{multiplier:.1f}x the engagement of {lowest_type}s in this account. "
        f"Best single post was a {best_post['post_type']} on "
        f"{best_post['date'].strftime('%b %d, %Y')} with {int(best_post['engagements'])} engagements — "
        f"worth studying what made that one different."
    )
    return recommendation


def _style_axes(ax):
    """Shared styling so every chart looks like it belongs in the same deck."""
    ax.tick_params(colors=GREY, labelsize=TICK_SIZE)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#333333")


def engagement_trend_chart(df, out_path=BASE_DIR / "chart_engagement_trend.png"):
    df_sorted = df.sort_values("date")
    fig, ax = plt.subplots(figsize=FIGSIZE, facecolor=BLACK)
    ax.set_facecolor(BLACK)
    ax.plot(df_sorted['date'], df_sorted['engagements'], color=ORANGE, marker="o", linewidth=2.5, markersize=7)
    ax.set_title("Engagement over time", color=WHITE, fontsize=TITLE_SIZE, pad=20, loc="left")
    _style_axes(ax)

    plt.tight_layout()
    plt.savefig(out_path, facecolor=BLACK, dpi=DPI)
    plt.close()
    print(f"Saved {out_path}")


def engagement_by_type_chart(df, out_path=BASE_DIR / "chart_engagement_by_type.png"):
    avg_by_type = df.groupby("post_type")["engagements"].mean().sort_values()

    fig, ax = plt.subplots(figsize=FIGSIZE, facecolor=BLACK)
    ax.set_facecolor(BLACK)
    ax.barh(avg_by_type.index, avg_by_type.values, color=ORANGE)
    ax.set_title("Average engagement by post type", color=WHITE, fontsize=TITLE_SIZE, pad=20, loc="left")
    _style_axes(ax)
    for i, v in enumerate(avg_by_type.values):
        ax.text(v + 1, i, f"{v:.0f}", color=WHITE, va="center", fontsize=LABEL_SIZE)

    plt.tight_layout()
    plt.savefig(out_path, facecolor=BLACK, dpi=DPI)
    plt.close()
    print(f"Saved {out_path}")


def posting_frequency_chart(df, out_path=BASE_DIR / "chart_posting_frequency.png"):
    """
    New: visualizes the posting cadence data that was already being
    calculated but never charted. This is what shows a business owner
    whether their inconsistency is real, and when it happened.
    """
    _, post_per_week = posting_frequency(df)

    fig, ax = plt.subplots(figsize=FIGSIZE, facecolor=BLACK)
    ax.set_facecolor(BLACK)
    ax.bar(post_per_week.index, post_per_week.values, color=ORANGE, width=5)
    ax.set_title("Posts per week", color=WHITE, fontsize=TITLE_SIZE, pad=20, loc="left")
    _style_axes(ax)

    avg_line = post_per_week.mean()
    ax.axhline(avg_line, color=GREY, linestyle="--", linewidth=1.5)
    ax.text(
        post_per_week.index[0], avg_line + 0.15,
        f"avg: {avg_line:.1f}/week", color=GREY, fontsize=12
    )

    plt.tight_layout()
    plt.savefig(out_path, facecolor=BLACK, dpi=DPI)
    plt.close()
    print(f"Saved {out_path}")


if __name__ == "__main__":
    df = load_data(CSV_PATH)

    print("=== POSTING FREQUENCY ===")
    post_per_month, post_per_week = posting_frequency(df)
    print(f"Avg posts/week:  {post_per_week.mean():.1f}")
    print(f"Avg posts/month: {post_per_month.mean():.1f}")

    print("\n=== ENGAGEMENT STATS ===")
    overall_avg, by_type_avg = engagement_stats(df)
    print(f"Overall average engagement: {overall_avg:.1f}")
    print("\nAverage engagement by post type:")
    print(by_type_avg)

    print("\n=== BEST / WORST POST ===")
    best, worst = best_worst_posts(df)
    print(f"Best:  {best['post_type']} on {best['date'].date()} — {int(best['engagements'])} engagements")
    print(f"Worst: {worst['post_type']} on {worst['date'].date()} — {int(worst['engagements'])} engagements")

    print("\n=== RECOMMENDATION ===")
    recommendation = generate_recommendation(by_type_avg, best)
    print(recommendation)

    engagement_trend_chart(df)
    engagement_by_type_chart(df)
    posting_frequency_chart(df)