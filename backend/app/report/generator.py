"""HTML/PDF report generator (Phase 4)."""

import datetime
from app.models.analysis import AnalysisResult


def generate_html_report(result: AnalysisResult) -> str:
    metrics = result.metrics
    
    savings_rate_display = f" ({metrics.savings_rate * 100:.1f}%)" if metrics.savings_rate is not None else ""
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RupeeRadar Report - {result.filename}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            .header {{ border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 20px; }}
            .summary-cards {{ display: flex; gap: 20px; margin-bottom: 30px; }}
            .card {{ flex: 1; padding: 15px; border: 1px solid #ddd; border-radius: 8px; background: #f9f9f9; }}
            .card-title {{ font-size: 14px; color: #666; margin-bottom: 5px; }}
            .card-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
            th, td {{ padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }}
            th {{ background-color: #f5f5f5; }}
            .amount {{ text-align: right; font-variant-numeric: tabular-nums; }}
            .debit {{ color: #e74c3c; }}
            .credit {{ color: #27ae60; }}
            .insight {{ background: #e8f4f8; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #3498db; }}
            @media print {{
                body {{ padding: 0; }}
                .page-break {{ page-break-before: always; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <h1 style="margin: 0;">RupeeRadar Financial Report</h1>
                </div>
                <p><strong>File:</strong> {result.filename}</p>
                <p><strong>Period:</strong> {metrics.period_start} to {metrics.period_end}</p>
                <p><strong>Generated:</strong> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
            </div>

            <h2>Executive Summary</h2>
            <div class="summary-cards">
                <div class="card">
                    <div class="card-title">Total Spend</div>
                    <div class="card-value">₹{metrics.total_spend:,.2f}</div>
                </div>
                <div class="card">
                    <div class="card-title">Total Income</div>
                    <div class="card-value">₹{metrics.total_income:,.2f}</div>
                </div>
                <div class="card">
                    <div class="card-title">Savings</div>
                    <div class="card-value">₹{metrics.savings:,.2f}{savings_rate_display}</div>
                </div>
            </div>

            <h2>Key Insights</h2>
    """
    
    for insight in result.insights:
        html += f"""
            <div class="insight">
                <strong>{insight.title}</strong>
                <p style="margin: 5px 0 0 0;">{insight.body}</p>
            </div>
        """
        
    html += """
            <h2>Category Breakdown (Spend)</h2>
            <table>
                <tr>
                    <th>Category</th>
                    <th class="amount">Amount</th>
                    <th class="amount">% of Total Spend</th>
                </tr>
    """
    
    sorted_categories = sorted(metrics.by_category.items(), key=lambda x: x[1], reverse=True)
    
    for category_name, spend in sorted_categories:
        if spend > 0:
            percentage = (spend / metrics.total_spend * 100) if metrics.total_spend > 0 else 0
            html += f"""
                <tr>
                    <td>{category_name}</td>
                    <td class="amount">₹{spend:,.2f}</td>
                    <td class="amount">{percentage:.1f}%</td>
                </tr>
            """
            
    html += """
            </table>
            
            <div class="page-break"></div>
            
            <h2>Top 5 Largest Debits</h2>
            <table>
                <tr>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Category</th>
                    <th class="amount">Amount</th>
                </tr>
    """
    
    debits = [t for t in result.transactions if t.type == 'debit']
    top_debits = sorted(debits, key=lambda x: x.amount, reverse=True)[:5]
    
    for debit in top_debits:
        html += f"""
                <tr>
                    <td>{debit.date}</td>
                    <td>{debit.description_clean or debit.description}</td>
                    <td>{debit.category.value if debit.category else 'Unknown'}</td>
                    <td class="amount debit">₹{debit.amount:,.2f}</td>
                </tr>
        """
        
    html += """
            </table>

            <h2>Recurring Payments Detected</h2>
    """
    
    if hasattr(result, 'recurring') and result.recurring:
        html += """
            <table>
                <tr>
                    <th>Merchant / Description</th>
                    <th>Type</th>
                    <th>Frequency</th>
                    <th class="amount">Monthly Est.</th>
                </tr>
        """
        for group in result.recurring:
            g_type = group.type.value if hasattr(group.type, "value") else str(group.type)
            g_freq = group.frequency.value if hasattr(group.frequency, "value") else str(group.frequency)
            html += f"""
                <tr>
                    <td>{group.label or 'Unknown'}</td>
                    <td>{g_type.title()}</td>
                    <td>{g_freq.title()}</td>
                    <td class="amount">₹{group.monthly_estimate:,.2f}</td>
                </tr>
            """
        html += "</table>"
    else:
        html += "<p>No recurring payments detected.</p>"

    html += """
        </div>
    </body>
    </html>
    """
    
    return html
