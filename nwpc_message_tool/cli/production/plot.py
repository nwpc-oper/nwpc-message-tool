import click
from loguru import logger

from nwpc_message_tool._util import get_engine
from nwpc_message_tool.cli._util import parse_start_time
from nwpc_message_tool.storage import EsMessageStorage, get_es_message_storage
from nwpc_message_tool.presenter.plot import (
    StepGridPlotPresenter,
    PeriodBarPlotPresenter,
)
from nwpc_message_tool.processor import TableProcessor


@click.command("plot")
@click.option("--plot-type", default="step_grid", type=click.Choice(["step_grid", "period_bar"]), help="type of plot")
@click.option("--elastic-server", multiple=True, help="ElasticSearch servers")
@click.option("--storage-name", help="Use storage which is set in config file. Default use ``default_storage`` key.")
@click.option("--system", required=True, help="system, such as grapes_gfs_gmf, grapes_meso_3km and so on.")
@click.option("--production-stream", default="oper", help="production stream, such as oper.")
@click.option("--production-type", default="grib2", help="production type, such as grib.")
@click.option("--production-name", default="orig", help="production name, such as orig.")
@click.option(
    "--start-time",
    required=True,
    metavar="YYYYMMDDHH[[/YYYYMMDDHH]|[,YYYYMMDDHH,...]]",
    help="start time, one date, a data range or a list of data.")
@click.option(
    "--start-time-freq",
    default="",
    help="start time range frequency, such as `D` means one point per day. "
         "If --start-time is YYYYMMDDHH/YYYYMMDDHH, "
         "use this option to generate a data list. "
         "See documentation of pandas.data_range for more detail."
)
@click.option(
    "--engine",
    default="nwpc_message",
    type=click.Choice(["nwpc_message", "nmc_monitor"]),
    help="data source"
)
@click.option(
    "--output-type",
    default="file",
    type=click.Choice(["file"]),
    help="output type, currently only file is supported. "
         "Once the plot is done, a html file is writen to disk and is opened by default web browser."
)
@click.option(
    "--output-file",
    help="output file path",
)
@click.option("--config-file", default=None, help="config file path, default is ``${HOME}/.config/nwpc-oper/nwpc-message-tool.yaml``.")
def plot_cli(
        plot_type,
        elastic_server,
        storage_name,
        system,
        production_stream,
        production_type,
        production_name,
        start_time: str,
        start_time_freq,
        engine,
        output_type,
        output_file,
        config_file,
):
    """
    Plot for production message.
    """
    start_time = parse_start_time(start_time, start_time_freq)

    engine = get_engine(engine)
    logger.info(f"using search engine: {engine.__name__}")

    system = engine.fix_system_name(system)
    logger.info(f"fix system name to: {system}")

    logger.info(f"searching...")
    if len(elastic_server) > 0:
        client = EsMessageStorage(
            hosts=elastic_server,
            show_progress=True
        )
    else:
        client = get_es_message_storage(
            storage_name,
            show_progress=True,
        )

    results = client.get_production_messages(
        system=system,
        production_stream=production_stream,
        production_type=production_type,
        production_name=production_name,
        start_time=start_time,
        engine=engine.production,
    )

    processor = TableProcessor()
    table = processor.process_messages(results)

    print(table)

    if plot_type == "step_grid":
        presenter = StepGridPlotPresenter(
            system=system,
            output_type=("file",),
            output_path=output_file,
        )
        presenter.show(table)
    elif plot_type == "period_bar":
        presenter = PeriodBarPlotPresenter(
            system=system,
            output_type=("file",),
            output_path=output_file,
        )
        presenter.show(table)
    else:
        raise ValueError(f"plot type is not supported: {plot_type}")


if __name__ == "__main__":
    plot_cli()
