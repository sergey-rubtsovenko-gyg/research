import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt


def plot_ts(df, tour_id, date_col='date', target_col='tickets'):
    demo_df = df[df['tour_id'] == tour_id]
    demo_df = demo_df.sort_values(by=date_col)
    fig = px.line(demo_df, x=date_col, y=target_col, title=f'tour_id={tour_id}', markers=True)
    fig.update_traces(marker=dict(size=4))
    return fig


def plot_tours_ts(df, tour_ids):
    for tour_id in tour_ids:
        print(f'tour_id: {tour_id}')
        fig = plot_ts(df=df, tour_id=tour_id)
        fig.show()


def plot_actual_and_forecast(df, tour_id, date_col='date', actual_col='tickets', forecast_col='forecast'):
    demo_df = df[df['tour_id'] == tour_id]
    demo_df = demo_df.sort_values(by=date_col)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=demo_df[date_col], y=demo_df[actual_col], mode='lines+markers', name='actual', marker=dict(size=4)
    ))
    fig.add_trace(go.Scatter(
        x=demo_df[date_col], y=demo_df[forecast_col], mode='lines+markers', name='forecast', marker=dict(size=4)
    ))

    fig.update_layout(title=f'tour_id={tour_id}')
    return fig