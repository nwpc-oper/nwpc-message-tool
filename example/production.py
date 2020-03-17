import datetime

import pandas as pd
import click
from loguru import logger

from nwpc_message_tool.storage import EsMessageStorage
from nwpc_message_tool.message import ProductionEventMessage


def get_hour(message: ProductionEventMessage) -> int:
    return int(message.forecast_time.seconds/3600) + message.forecast_time.days * 24


@click.command()
@click.option("--elastic-server", required=True, multiple=True, help="ElasticSearch servers")
@click.option("--system", required=True, help="system")
@click.option("--production-stream", default="oper", help="stream")
@click.option("--production-type", default="grib2", help="type")
@click.option("--production-name", default="orig", help="name")
@click.option("--start-time", required=True, help="name, YYYYMMDDHH")
def cli(elastic_server, system, production_stream, production_type, production_name, start_time):
    start_time = datetime.datetime.strptime(start_time, "%Y%m%d%H")

    client = EsMessageStorage(
        hosts=elastic_server,
    )
    results = client.get_production_messages(
        system=system,
        production_stream=production_stream,
        production_type=production_type,
        production_name=production_name,
        start_time=start_time
    )
    df = pd.DataFrame(columns=["time"])
    for result in results:
        hours = get_hour(result)
        message_time = result.time.ceil("S")
        current_df = pd.DataFrame({"time": [message_time]}, columns=["time"], index=[hours])
        df = df.append(current_df)

    logger.info("Get {} results", len(df))
    df = df.sort_index()
    print(df)
    print(f"Latest time: {df.time.max()}")


if __name__ == "__main__":
    cli()
