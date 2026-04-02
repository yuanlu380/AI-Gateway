"""
FinOps Dashboard - Standalone web app that displays the same data as the Azure Portal workbooks.
Run: python app.py
Access: http://localhost:8050
"""
import os, sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from flask import Flask, render_template, jsonify
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from datetime import timedelta
import json

app = Flask(__name__)

# --- Configuration (auto-detected from deployment) ---
RESOURCE_GROUP = os.environ.get("RESOURCE_GROUP", "lab-finops-framework")
DEPLOYMENT_NAME = os.environ.get("DEPLOYMENT_NAME", "finops-framework")

def get_workspace_id():
    """Get workspace ID from deployment outputs or environment variable."""
    ws_id = os.environ.get("LOG_ANALYTICS_WORKSPACE_ID")
    if ws_id:
        return ws_id
    # Auto-detect from deployment
    import subprocess
    result = subprocess.run(
        f'az deployment group show --name {DEPLOYMENT_NAME} -g {RESOURCE_GROUP} --query "properties.outputs.logAnalyticsWorkspaceId.value" -o tsv',
        capture_output=True, text=True, shell=True
    )
    return result.stdout.strip()

WORKSPACE_ID = get_workspace_id()

# --- KQL Queries (same as Azure Portal workbooks) ---
COST_SUMMARY_QUERY = """
let llmHeaderLogs = ApiManagementGatewayLlmLog
| where TimeGenerated >= startofmonth(now()) and TimeGenerated <= endofmonth(now())
| where DeploymentName != '';
let llmLogsWithSubscriptionId = llmHeaderLogs
| join kind=leftouter ApiManagementGatewayLogs on CorrelationId
| project
    SubscriptionName = ApimSubscriptionId, DeploymentName, PromptTokens, CompletionTokens, TotalTokens;
llmLogsWithSubscriptionId
| join kind=inner (
    PRICING_CL
    | summarize arg_max(TimeGenerated, *) by Model
    | project Model, InputTokensPrice, OutputTokensPrice
    )
    on $left.DeploymentName == $right.Model
| extend InputCost = PromptTokens * InputTokensPrice
| extend OutputCost = CompletionTokens * OutputTokensPrice
| summarize
    InputCost = sum(InputCost), OutputCost = sum(OutputCost)
    by SubscriptionName
| extend TotalCost = (InputCost + OutputCost) / 1000
| join kind=inner (
    SUBSCRIPTION_QUOTA_CL
    | summarize arg_max(TimeGenerated, *) by Subscription
    | project Subscription, CostQuota
) on $left.SubscriptionName == $right.Subscription
| project SubscriptionName, CostQuota, TotalCost
| order by SubscriptionName asc
"""

COST_TREND_QUERY = """
let llmHeaderLogs = ApiManagementGatewayLlmLog
| where DeploymentName != '';
let llmLogsWithSubscriptionId = llmHeaderLogs
| join kind=leftouter ApiManagementGatewayLogs on CorrelationId
| project
    TimeGenerated, SubscriptionName = ApimSubscriptionId, DeploymentName, PromptTokens, CompletionTokens, TotalTokens;
llmLogsWithSubscriptionId
| join kind=inner (
    PRICING_CL
    | summarize arg_max(TimeGenerated, *) by Model
    | project Model, InputTokensPrice, OutputTokensPrice
    )
    on $left.DeploymentName == $right.Model
| extend InputCost = PromptTokens * InputTokensPrice
| extend OutputCost = CompletionTokens * OutputTokensPrice
| summarize
    InputCost = sum(InputCost), OutputCost = sum(OutputCost)
    by SubscriptionName, bin(TimeGenerated, 1m)
| extend TotalCost = (InputCost + OutputCost) / 1000
| project TimeGenerated, SubscriptionName, TotalCost
| order by TimeGenerated asc
"""

TOKEN_USAGE_QUERY = """
ApiManagementGatewayLlmLog
| where DeploymentName != ''
| join kind=leftouter ApiManagementGatewayLogs on CorrelationId
| summarize
    PromptTokens = sum(PromptTokens),
    CompletionTokens = sum(CompletionTokens),
    TotalTokens = sum(TotalTokens),
    Requests = count()
    by SubscriptionName = ApimSubscriptionId
| order by SubscriptionName asc
"""

REQUEST_STATS_QUERY = """
ApiManagementGatewayLogs
| where OperationId != ''
| summarize
    TotalRequests = count(),
    SuccessfulRequests = countif(ResponseCode >= 200 and ResponseCode < 400),
    FailedRequests = countif(ResponseCode >= 400),
    AvgLatencyMs = avg(TotalTime)
    by bin(TimeGenerated, 5m)
| order by TimeGenerated asc
"""


def run_query(query, timespan=timedelta(hours=4)):
    """Execute a KQL query against Log Analytics."""
    try:
        credential = DefaultAzureCredential()
        client = LogsQueryClient(credential)
        response = client.query_workspace(WORKSPACE_ID, query, timespan=timespan)
        if response.status == LogsQueryStatus.SUCCESS:
            table = response.tables[0]
            if not table.columns:
                return {"columns": [], "rows": [], "error": None}
            columns = list(table.columns)
            rows = [dict(zip(columns, row)) for row in table.rows]
            return {"columns": columns, "rows": rows, "error": None}
        else:
            return {"columns": [], "rows": [], "error": str(response.partial_error)}
    except Exception as e:
        return {"columns": [], "rows": [], "error": str(e)}


def safe_serialize(obj):
    """JSON-serialize with handling for special types."""
    import datetime
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if isinstance(obj, timedelta):
        return str(obj)
    return str(obj)


@app.route("/")
def dashboard():
    return render_template("dashboard.html",
        workspace_id=WORKSPACE_ID,
        resource_group=RESOURCE_GROUP,
    )


@app.route("/api/refresh")
def refresh_data():
    """API endpoint to get fresh data as JSON."""
    cost_summary = run_query(COST_SUMMARY_QUERY, timespan=timedelta(days=30))
    cost_trend = run_query(COST_TREND_QUERY, timespan=timedelta(hours=4))
    token_usage = run_query(TOKEN_USAGE_QUERY, timespan=timedelta(hours=4))
    request_stats = run_query(REQUEST_STATS_QUERY, timespan=timedelta(hours=4))

    result = {
        "costSummary": cost_summary["rows"],
        "costTrend": cost_trend["rows"],
        "tokenUsage": token_usage["rows"],
        "requestStats": request_stats["rows"],
    }
    return app.response_class(
        response=json.dumps(result, default=safe_serialize),
        mimetype='application/json'
    )


if __name__ == "__main__":
    print(f"🚀 FinOps Dashboard starting...")
    print(f"   Workspace ID: {WORKSPACE_ID}")
    print(f"   Resource Group: {RESOURCE_GROUP}")
    print(f"   Open: http://localhost:8050")
    app.run(host="0.0.0.0", port=8050, debug=True)
