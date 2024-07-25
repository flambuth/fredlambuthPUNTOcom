from app import utils
from app.dash_plotlys import data_sources, plotly_figures
from datetime import timedelta

def twenty_4_hrs_N_days_ago(N):
    
    blob_date = utils.pick_days_ago_from_today(N)
    date_obj, am,pm = data_sources.polar_chart_ingredients(blob_date)
    fig = plotly_figures.polar_chart_of_am_pm(
        date_obj, am, pm
    )
    return fig

def date_into_polar_chart(date_obj):
    date_obj, am,pm = data_sources.polar_chart_ingredients(date_obj)
    fig = plotly_figures.polar_chart_of_am_pm(
        date_obj, am, pm
    )
    return fig


def set_theta_range_of_polar(date_objs):
    ingredients = list(map(
        data_sources.polar_chart_ingredients,
        date_objs
    ))
    biggest_theta = max([max(ingredient[1]+ingredient[2]) for ingredient in ingredients])
    return biggest_theta


def week_of_polar_charts(monday_start_date):
    six_days_from_now = timedelta(days=6)
    end_date = monday_start_date + six_days_from_now

    date_objs = []
    current_date = monday_start_date

    while current_date <= end_date:
        date_objs.append(current_date)
        current_date += timedelta(days=1)

    max_range = set_theta_range_of_polar(date_objs)

    week_figs = list(map(
        date_into_polar_chart,
        date_objs
    ))

    sevenFig = plotly_figures.seven_days_of_polar_charts(week_figs, monday_start_date, max_range)

    return sevenFig