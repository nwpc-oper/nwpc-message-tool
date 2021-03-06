import typing

import pandas as pd

from nwpc_message_tool.presenter.presenter import Presenter


class TableStorePresenter(Presenter):
    """
    Save message table generated by ``TableProcessor`` into files.

    Attributes
    ----------
    output_type : str
        output type, supported types:

        - ``csv``
        - ``json``
    output_path :
        output file path,
    """
    def __init__(
            self,
            output_type: str,
            output_file: str
    ):
        super(TableStorePresenter, self).__init__()
        self.output_type = output_type
        self.output_file = output_file

    def show(self, df: pd.DataFrame):
        if self.output_type == "csv":
            df.to_csv(self.output_file)
        elif self.output_type == "json":
            df.to_json(self.output_file)
        else:
            raise ValueError(f"output type is not supported: {self.output_type}")
