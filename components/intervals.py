import dash

initial_refresh_interval_id = "refresh-cluster-initial"
initial_refresh_interval = dash.dcc.Interval(
    id=initial_refresh_interval_id,
    interval=10,  # in milliseconds,
    max_intervals=1,
    n_intervals=0,
)

long_refresh_interval_id = "refresh-cluster-long"
long_refresh_interval = dash.dcc.Interval(
    id=long_refresh_interval_id,
    interval=1 * 30 * 1000,  # in milliseconds,
    max_intervals=120,  # run for 1 hour
    n_intervals=0,
)
