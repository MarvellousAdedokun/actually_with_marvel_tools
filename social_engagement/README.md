# Instagram Engagement Analysis: The African Braiding Bar vs. Braids by the Nigerian Sistas

**[INSERT ONE-LINE FINDING — e.g. "The African Braiding Bar is getting X% less engagement per post than its closest local competitor, and hasn't posted since April."]**

This is a free, public breakdown of what two competing hair-braiding businesses' own public Instagram data says about their content strategy — part of an ongoing series analyzing real businesses using only data they've already made public. Full write-up and methodology below.

---

## The headline

[PASTE the competitive recommendation paragraph from recommendation.txt here — the "X is averaging Y% more engagement than Z" line]

---

## What the data shows

### Posting frequency vs. engagement

![Client: frequency vs engagement](chart_client_frequency_vs_engagement.png)
![Competitor: frequency vs engagement](chart_competitor_frequency_vs_engagement.png)

[1-2 sentences: what pattern is visible — gaps, consistency, correlation with engagement]

### Engagement by post type

![Client: engagement by type](chart_client_engagement_by_type.png)
![Competitor: engagement by type](chart_competitor_engagement_by_type.png)

[1-2 sentences: which format wins for each business, and whether that's a real signal or a mono-format artifact — check your dominant_format() caveat here]

### Head-to-head

![Business comparison](chart_business_comparison.png)

[1 sentence tying it back to the headline finding]

---

## Full recommendation

[PASTE the full contents of recommendation.txt here — internal recommendation for each business, plus the competitive comparison]

---

## Methodology

- **Data source:** Public Instagram post data (likes, comments, shares, post type, date) — manually logged from each business's public profile. No private analytics, no scraping tools, no login access to either account.
- **Date range:** [INSERT — e.g. "Dec 2025–Sept 2026"]
- **Engagement score:** likes + comments + shares (saves excluded — not consistently visible across post types on Instagram)
- **Sample size:** [INSERT post counts per business]

## Limitations

- Engagement is a proxy for attention, not for bookings, revenue, or conversion — this data can't confirm whether either business is actually converting that attention into paying customers.
- Where one business relies heavily on a single post format, its type-vs-type comparison reflects a lack of experimentation, not proof that the format is optimal.
- Any type-level comparison below 5 posts per type is flagged as unreliable rather than reported as a finding.

## Disclaimer

This is an independent analysis based on publicly available Instagram data. It is not affiliated with, commissioned by, or endorsed by The African Braiding Bar or Braids by the Nigerian Sistas.

---

## Tech

Python (pandas, matplotlib). Script: [`social_pipeline.py`](./social_pipeline.py). Reusable across businesses — just supply two CSVs in the same schema (`date, post_type, likes, comments, shares`).

Part of an ongoing series analyzing public business data to find decisions, not just dashboards. More at [@adedokun_marvellous](https://instagram.com/adedokun_marvellous).
