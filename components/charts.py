
import plotly.express as px


def create_period_comparison_chart(df, dimension_column):

    chart_df = df.melt(
        id_vars=[dimension_column],
        value_vars=["Previous Value", "Current Value"],
        var_name="Period",
        value_name="Value"
    )

    fig = px.bar(
        chart_df,
        x=dimension_column,
        y="Value",
        color="Period",
        barmode="group",
        title="Previous vs Current Period by Segment",
        text_auto=True
    )

    fig.update_layout(
        xaxis_title=dimension_column,
        yaxis_title="Business Metric",
        legend_title="Period",
        template="plotly_dark"
    )

    return fig


def create_contribution_chart(df, dimension_column):

    fig = px.bar(
        df,
        x=dimension_column,
        y="Change",
        color="Change",
        color_continuous_scale="RdYlGn",
        title="Segment Contribution to Business Change",
        text_auto=True
    )

    fig.update_layout(
        xaxis_title=dimension_column,
        yaxis_title="Absolute Change",
        template="plotly_dark"
    )

    fig.add_hline(y=0, line_dash="dash")

    return fig
