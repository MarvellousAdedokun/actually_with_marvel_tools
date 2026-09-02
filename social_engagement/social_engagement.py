import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# --- Business config: fill these in ---
CLIENT_NAME = "The African Braiding Bar IG"
CLIENT_CSV = BASE_DIR / "client_posts.csv"

COMPETITOR_NAME = "Braids by the Nigerian Sistas"
COMPETITOR_CSV = BASE_DIR / "competitor_posts.csv"

ORANGE = "#E8630A"
BLACK = "#0A0A0A"
WHITE = "#FFFFFF"
GREY = "#999999"
COMPETITOR_GREY = "#555555"

FIGSIZE = (12, 7)
TITLE_SIZE = 22
LABEL_SIZE = 14
TICK_SIZE = 13
DPI = 300

# Columns summed into a single engagement score. Not every platform export
# has all four (e.g. some don't expose "saves") — only sum what's present
# so this doesn't break on a different business's CSV.
ENGAGEMENT_COLUMNS = ["likes", "comments", "shares", "saves"]

MIN_SAMPLE_PER_TYPE = 5  # below this, don't trust a type-vs-type comparison


def load_data(csv_path):
    df = pd.read_csv(csv_path)

    # Some exports have a trailing blank line that reads in as an
    # all-NaN row — drop it before it corrupts date parsing / groupby.
    df = df.dropna(how="all")

    # Dates come as dd/mm/yyyy. Without dayfirst=True, pandas infers the
    # format per-file from whichever rows are unambiguous (day > 12) and
    # then applies that guess to everything else — for a file where every
    # day happens to be <= 12 it could silently guess mm/dd instead and
    # swap month/day on every row with no error. Being explicit removes
    # the guesswork instead of trusting the inference to get it right.
    df["date"] = pd.to_datetime(df["date"], dayfirst=True)

    # Post type casing is inconsistent between (and even within) exports
    # ("video" vs "Video" vs "Video Carousel"/"Picture Carousel"). Left
    # as-is, groupby("post_type") splits what's really one category into
    # two, which quietly dilutes sample sizes below MIN_SAMPLE_PER_TYPE
    # and skews the by-type averages. Normalize casing/whitespace so the
    # same content type is always counted as one group.
    df["post_type"] = df["post_type"].str.strip().str.title()

    present_cols = [c for c in ENGAGEMENT_COLUMNS if c in df.columns]
    missing_cols = [c for c in ENGAGEMENT_COLUMNS if c not in df.columns]
    if missing_cols:
        print(f"Note: {missing_cols} not found in this dataset — engagement score uses {present_cols} only.")

    df["engagements"] = df[present_cols].sum(axis=1)
    return df


def posting_frequency(df, end_date=None):
    """
    How many posts per week/month — is posting consistent or sporadic?

    Grouping with pd.Grouper only produces bins for periods that actually
    contain a row, so a business that stopped posting months ago just has
    its series stop — silence reads as "no data" instead of "zero posts."
    To surface real dead air, we reindex both series across the full range
    from the earliest post through `end_date` (defaults to today), filling
    the gaps with 0.
    """
    if end_date is None:
        end_date = pd.Timestamp.today()
    end_date = pd.Timestamp(end_date)

    start_date = df["date"].min()

    post_per_month = df.groupby(pd.Grouper(key="date", freq="ME")).size()
    full_months = pd.date_range(start_date, end_date, freq="ME")
    post_per_month = post_per_month.reindex(full_months, fill_value=0)

    post_per_week = df.groupby(pd.Grouper(key="date", freq="W")).size()
    full_weeks = pd.date_range(start_date, end_date, freq="W")
    post_per_week = post_per_week.reindex(full_weeks, fill_value=0)

    return post_per_month, post_per_week


def engagement_stats(df):
    """
    Average engagement overall, and broken down by post type.
    """
    overall_avg = df["engagements"].mean()
    by_type_avg = df.groupby("post_type")["engagements"].mean().sort_values(ascending=False)
    return overall_avg, by_type_avg


def best_worst_posts(df):
    """
    Identify the single best- and worst-performing post by engagement.
    """
    best = df.loc[df["engagements"].idxmax()]
    worst = df.loc[df["engagements"].idxmin()]
    return best, worst


def generate_recommendation(by_type_avg, best_post, post_per_week, type_counts, min_sample=MIN_SAMPLE_PER_TYPE):
    """
    Multi-factor, written recommendation based on the business's OWN data.
    Checks posting consistency AND post-type performance, and refuses
    to make a type-vs-type claim when the sample size doesn't support it.
    """
    lines = []

    avg_weekly = post_per_week.mean()
    std_weekly = post_per_week.std()
    zero_weeks = int((post_per_week == 0).sum())
    total_weeks = len(post_per_week)

    if total_weeks and zero_weeks / total_weeks > 0.25:
        lines.append(
            f"Posting is inconsistent — {zero_weeks} of {total_weeks} weeks had zero posts. "
            f"Fix the gaps before optimizing post type: inconsistent posting resets reach "
            f"every time, so even the best-performing format won't compound."
        )
    elif avg_weekly > 0 and std_weekly > avg_weekly * 0.75:
        lines.append(
            f"Posting cadence is volatile (avg {avg_weekly:.1f}/week, swings widely week to week). "
            f"A steadier rhythm is likely worth more right now than switching formats."
        )

    valid_types = type_counts[type_counts >= min_sample].index
    filtered = by_type_avg[by_type_avg.index.isin(valid_types)]

    if len(filtered) >= 2:
        top_type, top_avg = filtered.index[0], filtered.iloc[0]
        low_type, low_avg = filtered.index[-1], filtered.iloc[-1]
        multiplier = top_avg / low_avg if low_avg > 0 else float("inf")
        lines.append(
            f"Among post types with enough data to trust ({', '.join(valid_types)}), "
            f"{top_type}s earn {multiplier:.1f}x the engagement of {low_type}s — shift weight toward {top_type}s."
        )
    else:
        lines.append(
            f"Not enough posts per type yet (need {min_sample}+ each) to trust a type-vs-type "
            f"comparison — flag this as a gap rather than force a conclusion."
        )

    lines.append(
        f"Best single post was a {best_post['post_type']} on "
        f"{best_post['date'].strftime('%b %d, %Y')} with {int(best_post['engagements'])} engagements — "
        f"worth reverse-engineering what made that one different."
    )

    return "\n\n".join(lines)


def compare_businesses(business_dfs: dict):
    """
    business_dfs: {"Business Name": df, ...}
    Returns a summary DataFrame — avg engagement per post and avg posts/week
    for each business, side by side. This is what makes the recommendation
    competitive instead of just internal.
    """
    rows = []
    for name, df in business_dfs.items():
        overall_avg, _ = engagement_stats(df)
        _, post_per_week = posting_frequency(df)
        rows.append({
            "business": name,
            "avg_engagement": overall_avg,
            "avg_posts_per_week": post_per_week.mean(),
        })
    return pd.DataFrame(rows).set_index("business")


def generate_competitive_recommendation(summary_df, client_name):
    """
    The line that actually lands: not 'here's your engagement' but
    'here's your engagement next to the competitor you're losing attention to.'
    """
    if client_name not in summary_df.index or len(summary_df) < 2:
        return None

    client_row = summary_df.loc[client_name]
    others = summary_df.drop(client_name)
    best_competitor = others["avg_engagement"].idxmax()
    best_row = others.loc[best_competitor]

    if best_row["avg_engagement"] > client_row["avg_engagement"]:
        gap = (best_row["avg_engagement"] / client_row["avg_engagement"] - 1) * 100
        posting_note = (
            "despite posting less often" if best_row["avg_posts_per_week"] < client_row["avg_posts_per_week"]
            else "while posting more often"
        )
        return (
            f"{best_competitor} is averaging {gap:.0f}% more engagement per post than {client_name}, "
            f"{posting_note} ({best_row['avg_posts_per_week']:.1f} vs {client_row['avg_posts_per_week']:.1f} "
            f"posts/week). That gap is the real story — it's not about posting more, it's about what's "
            f"earning attention once {client_name} does post."
        )
    else:
        gap = (client_row["avg_engagement"] / best_row["avg_engagement"] - 1) * 100
        return (
            f"{client_name} already outperforms {best_competitor} by {gap:.0f}% average engagement per post. "
            f"The opportunity isn't catching up — it's converting that attention advantage into actual "
            f"bookings, which engagement data alone can't confirm."
        )


def _style_axes(ax):
    """Shared styling so every chart looks like it belongs in the same deck."""
    ax.tick_params(colors=GREY, labelsize=TICK_SIZE)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#333333")


def engagement_by_type_chart(df, out_path):
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


def frequency_vs_engagement_chart(df, out_path):
    """
    One chart instead of two separate 'over time' views (old trend chart +
    old frequency chart). Cadence (bars) and average engagement (line) on
    the same weekly timeline, so gaps and dips can be read against each
    other directly — that correlation is what a raw post-history scroll
    on the platform itself can't show you.
    """
    _, post_per_week = posting_frequency(df)
    engagement_per_week = df.groupby(pd.Grouper(key="date", freq="W"))["engagements"].mean()
    # Reindex to the same full range as post_per_week so dead weeks show up
    # as gaps here too, instead of the line just stopping while the bars
    # keep going to zero. NaN (not 0) for weeks with no posts — there's no
    # "average engagement of zero," there's just nothing to average, and a
    # plotted 0 would misleadingly look like a post that flopped.
    engagement_per_week = engagement_per_week.reindex(post_per_week.index)

    fig, ax1 = plt.subplots(figsize=FIGSIZE, facecolor=BLACK)
    ax1.set_facecolor(BLACK)

    ax1.bar(post_per_week.index, post_per_week.values, color=ORANGE, width=5, label="Posts/week")
    ax1.set_title("Posting frequency vs. engagement, weekly", color=WHITE, fontsize=TITLE_SIZE, pad=20, loc="left")
    ax1.set_ylabel("Posts per week", color=ORANGE, fontsize=LABEL_SIZE)
    _style_axes(ax1)

    ax2 = ax1.twinx()
    ax2.plot(
        engagement_per_week.index, engagement_per_week.values,
        color=WHITE, marker="o", linewidth=2.5, markersize=6, label="Avg engagement/week"
    )
    ax2.set_ylabel("Avg engagement", color=WHITE, fontsize=LABEL_SIZE)
    ax2.tick_params(colors=GREY, labelsize=TICK_SIZE)
    ax2.spines["top"].set_visible(False)

    plt.tight_layout()
    plt.savefig(out_path, facecolor=BLACK, dpi=DPI)
    plt.close()
    print(f"Saved {out_path}")


def business_comparison_chart(summary_df, client_name, out_path):
    """
    The headline chart: client vs. competitor(s) on avg engagement per post.
    Client bar is always orange, competitors are grey, regardless of who wins —
    the color marks 'which one is you,' not 'who's winning.'
    """
    sorted_df = summary_df.sort_values("avg_engagement")
    colors = [ORANGE if idx == client_name else COMPETITOR_GREY for idx in sorted_df.index]

    fig, ax = plt.subplots(figsize=FIGSIZE, facecolor=BLACK)
    ax.set_facecolor(BLACK)
    ax.barh(sorted_df.index, sorted_df["avg_engagement"], color=colors)
    ax.set_title("Average engagement per post: you vs. competitor(s)", color=WHITE, fontsize=TITLE_SIZE, pad=20, loc="left")
    _style_axes(ax)
    for i, v in enumerate(sorted_df["avg_engagement"].values):
        ax.text(v + 1, i, f"{v:.0f}", color=WHITE, va="center", fontsize=LABEL_SIZE)

    plt.tight_layout()
    plt.savefig(out_path, facecolor=BLACK, dpi=DPI)
    plt.close()
    print(f"Saved {out_path}")


def save_text(text, out_path):
    out_path.write_text(text)
    print(f"Saved {out_path}")


def run_single_business_analysis(df, name, prefix):
    """Runs the full internal (non-competitive) analysis for one business."""
    print(f"\n{'=' * 10} {name.upper()} {'=' * 10}")

    print("=== POSTING FREQUENCY ===")
    post_per_month, post_per_week = posting_frequency(df)
    print(f"Avg posts/week:  {post_per_week.mean():.1f}")
    print(f"Avg posts/month: {post_per_month.mean():.1f}")

    print("\n=== ENGAGEMENT STATS ===")
    overall_avg, by_type_avg = engagement_stats(df)
    print(f"Overall average engagement: {overall_avg:.1f}")
    print(by_type_avg)

    print("\n=== BEST / WORST POST ===")
    best, worst = best_worst_posts(df)
    print(f"Best:  {best['post_type']} on {best['date'].date()} — {int(best['engagements'])} engagements")
    print(f"Worst: {worst['post_type']} on {worst['date'].date()} — {int(worst['engagements'])} engagements")

    print("\n=== RECOMMENDATION (internal) ===")
    type_counts = df["post_type"].value_counts()
    recommendation = generate_recommendation(by_type_avg, best, post_per_week, type_counts)
    print(recommendation)

    engagement_by_type_chart(df, BASE_DIR / f"chart_{prefix}_engagement_by_type.png")
    frequency_vs_engagement_chart(df, BASE_DIR / f"chart_{prefix}_frequency_vs_engagement.png")

    return recommendation


if __name__ == "__main__":
    client_df = load_data(CLIENT_CSV)
    client_recommendation = run_single_business_analysis(client_df, CLIENT_NAME, "client")

    business_dfs = {CLIENT_NAME: client_df}
    final_text = [f"=== {CLIENT_NAME}: internal analysis ===\n{client_recommendation}"]

    if COMPETITOR_CSV.exists():
        competitor_df = load_data(COMPETITOR_CSV)
        competitor_recommendation = run_single_business_analysis(competitor_df, COMPETITOR_NAME, "competitor")
        business_dfs[COMPETITOR_NAME] = competitor_df
        final_text.append(f"\n=== {COMPETITOR_NAME}: internal analysis ===\n{competitor_recommendation}")

        print(f"\n{'=' * 10} COMPETITIVE COMPARISON {'=' * 10}")
        summary_df = compare_businesses(business_dfs)
        print(summary_df)

        competitive_recommendation = generate_competitive_recommendation(summary_df, CLIENT_NAME)
        print(f"\n{competitive_recommendation}")
        final_text.append(f"\n=== Competitive comparison ===\n{competitive_recommendation}")

        business_comparison_chart(summary_df, CLIENT_NAME, BASE_DIR / "chart_business_comparison.png")
    else:
        print(f"\nNo competitor CSV found at {COMPETITOR_CSV} — skipping competitive comparison.")

    save_text("\n\n".join(final_text), BASE_DIR / "recommendation.txt")