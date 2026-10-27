
from pathlib import Path
import pandas as pd
from html import escape

# 1. Locate files beside this Python script
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "sales_data.csv"
OUTPUT_FILE = BASE_DIR / "monthly_report.html"

# 2. Load and validate the sample data
df = pd.read_csv(INPUT_FILE)

required = {"Month", "Revenue", "Expenses"}
if not required.issubset(df.columns):
    raise ValueError("CSV must contain Month, Revenue, Expenses.")

if df.empty:
    raise ValueError("The CSV contains no data.")

df["Revenue"] = pd.to_numeric(df["Revenue"], errors="raise")
df["Expenses"] = pd.to_numeric(df["Expenses"], errors="raise")

if (df["Revenue"] < 0).any() or (df["Expenses"] < 0).any():
    raise ValueError("Revenue and expenses must be non-negative.")

# 3. Calculate business metrics
df["Profit"] = df["Revenue"] - df["Expenses"]
df["Profit Margin"] = (
    df["Profit"].div(df["Revenue"].where(df["Revenue"] != 0)) * 100
)

latest = df.iloc[-1]
previous = df.iloc[-2] if len(df) > 1 else None

revenue = float(latest["Revenue"])
expenses = float(latest["Expenses"])
profit = float(latest["Profit"])
margin = latest["Profit Margin"]

# Revenue growth needs a previous month and nonzero previous revenue
if previous is not None and previous["Revenue"] != 0:
    growth = (
        (revenue - float(previous["Revenue"]))
        / float(previous["Revenue"]) * 100
    )
    growth_text = f"{growth:+.2f}%"
    growth_note = (
        "increased" if growth > 0 else
        "decreased" if growth < 0 else "was unchanged"
    )
else:
    growth = None
    growth_text = "N/A"
    growth_note = "cannot be calculated"

margin_text = f"{margin:.2f}%" if pd.notna(margin) else "N/A"

# 4. Build a simple month-by-month table
rows = ""
for _, item in df.iterrows():
    month = escape(str(item["Month"]))
    month_profit = float(item["Profit"])
    month_margin = item["Profit Margin"]
    month_margin_text = (
        f"{month_margin:.2f}%" if pd.notna(month_margin) else "N/A"
    )

    rows += f"""
    <tr>
      <td>{month}</td>
      <td>₹{item['Revenue']:,.0f}</td>
      <td>₹{item['Expenses']:,.0f}</td>
      <td>₹{month_profit:,.0f}</td>
      <td>{month_margin_text}</td>
    </tr>
    """

# 5. Create a business insight
if profit < 0:
    insight = "This month recorded a loss. Review expenses and pricing."
elif growth is not None and growth > 0:
    insight = (
        f"Revenue increased by {growth:.2f}% compared with the "
        "previous month. Review which products or activities "
        "contributed to the increase."
    )
elif growth is not None and growth < 0:
    insight = (
        f"Revenue decreased by {abs(growth):.2f}% compared with "
        "the previous month. Investigate the cause of the decline."
    )
else:
    insight = "Review the monthly trend to identify business changes."

# 6. Generate an HTML email-style report
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VP Freelance Monthly Report</title>
</head>
<body style="margin:0;background:#f3f5f4;font-family:Arial,sans-serif;color:#202820;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"
       style="background:#f3f5f4;padding:24px 8px;">
<tr><td align="center">
<table role="presentation" width="640" cellpadding="0" cellspacing="0"
       style="max-width:640px;width:100%;background:#ffffff;">
<tr><td style="background:#163c2b;color:white;padding:26px;">
<h1 style="margin:0;font-size:24px;">VP Freelance</h1>
<p style="margin:8px 0 0;">Monthly Business Performance Report</p>
</td></tr>
<tr><td style="padding:24px;">
<p>Hello,</p>
<p>Here is the business performance summary for
<strong>{escape(str(latest["Month"]))}</strong>.</p>

<table role="presentation" width="100%" cellpadding="8" cellspacing="0">
<tr>
<td style="background:#eef5ef;border:1px solid #dce8dd;">
<small>Revenue</small><br>
<strong>₹{revenue:,.0f}</strong>
</td>
<td style="background:#eef5ef;border:1px solid #dce8dd;">
<small>Expenses</small><br>
<strong>₹{expenses:,.0f}</strong>
</td>
</tr>
<tr>
<td style="background:#eef5ef;border:1px solid #dce8dd;">
<small>Net Profit</small><br>
<strong>₹{profit:,.0f}</strong>
</td>
<td style="background:#eef5ef;border:1px solid #dce8dd;">
<small>Profit Margin</small><br>
<strong>{margin_text}</strong>
</td>
</tr>
</table>

<h2 style="font-size:18px;margin-top:28px;">Monthly Performance</h2>
<table width="100%" cellpadding="8" cellspacing="0"
       style="border-collapse:collapse;font-size:13px;">
<tr style="background:#163c2b;color:white;">
<th align="left">Month</th><th align="right">Revenue</th>
<th align="right">Expenses</th><th align="right">Profit</th>
<th align="right">Margin</th>
</tr>
{rows}
</table>

<h2 style="font-size:18px;margin-top:28px;">Business Insight</h2>
<p>{escape(insight)}</p>
<p><strong>Revenue growth:</strong> {growth_text}</p>

<p style="font-size:12px;color:#657065;margin-top:28px;">
Demo report created using fictional sample data for portfolio
demonstration only. It is not a real client report.
</p>
<p style="font-size:12px;color:#657065;">
Prepared by VP Freelance | Data. Insights. Automation. Growth.
</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>
"""

# 7. Save the report
OUTPUT_FILE.write_text(html, encoding="utf-8")
print(f"Report created successfully: {OUTPUT_FILE}")
