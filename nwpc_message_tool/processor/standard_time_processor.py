import typing

import pandas as pd
from loguru import logger
from tqdm.auto import tqdm


class StandardTimeProcessor(object):
    def __init__(
            self,
            start_hours: typing.List,
            bootstrap_count: int = 1000,
            bootstrap_sample: int = 10,
            quantile: float = 0.99,
    ):
        self.start_hours = start_hours
        self.bootstrap_count = bootstrap_count
        self.bootstrap_sample = bootstrap_sample
        self.quantile = quantile

    def process_data(self, table: pd.DataFrame) -> typing.List:
        table["start_hour"] = table["start_time"].apply(lambda x: x.strftime("%H"))
        table["clock"] = table["time"] - table["start_time"]

        times = []

        for item in self.start_hours:
            start_hour = item["start_hour"]
            forecast_hours = item["forecast_hours"]
            df_start_hour = table[table["start_hour"] == start_hour][["forecast_hour", "clock"]]
            standard_times = []

            for hour_index in tqdm(range(len(forecast_hours)), desc=f"{start_hour} hour loop"):
                forecast_hour = forecast_hours[hour_index]
                clock_df_hour = df_start_hour[df_start_hour["forecast_hour"] == forecast_hour]
                means = []
                for i in range(self.bootstrap_count):
                    sampled_data = clock_df_hour["clock"].sample(
                        n=self.bootstrap_sample,
                        replace=True,
                    )
                    means.append(sampled_data.mean())

                bdf = pd.DataFrame(means).applymap(lambda x: x.ceil("s"))
                upper_bound = bdf.quantile(
                    self.quantile + (1 - self.quantile) / 2,
                    numeric_only=False,
                    interpolation="nearest"
                )
                lower_bound = bdf.quantile(
                    (1 - self.quantile) / 2,
                    numeric_only=False,
                    interpolation="nearest",
                )
                standard_times.append({
                    "forecast_hour": forecast_hour,
                    "upper_bound": upper_bound[0],
                    "lower_bound": lower_bound[0],
                })
            times.append({
                "start_hour": start_hour,
                "times": standard_times,
            })

        prod_time_dfs = [
            pd.DataFrame(a_time["times"]) for a_time in times
        ]

        for df in prod_time_dfs:
            df["upper_duration"] = df["upper_bound"].apply(lambda x: x.isoformat())
            df["lower_duration"] = df["lower_bound"].apply(lambda x: x.isoformat())

        production_times = [
            {
                "start_hour": self.start_hours[index]["start_hour"],
                "times": df[["forecast_hour", "upper_duration", "lower_duration"]].to_dict(orient="record")
            } for index, df in enumerate(prod_time_dfs)
        ]

        return production_times