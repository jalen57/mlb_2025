import math
import os
import sys
from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import List

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from tqdm import tqdm


load_dotenv('../../../.env', verbose=True, override=True)

# load database credentials
engine = create_engine(
    f"mysql+mysqlconnector://{os.environ['DB_USERNAME']}:{os.environ['DB_PASSWORD']}"
    f"@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
)


import math
import os
import sys
from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import List

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import text
from tqdm import tqdm


load_dotenv('../../../.env', verbose=True, override=True)

# load database credentials
engine = create_engine(
    f"mysql+mysqlconnector://{os.environ['DB_USERNAME']}:{os.environ['DB_PASSWORD']}"
    f"@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
)


def record_to_table(
    df: pd.DataFrame, table: str, verbose: bool = False
) -> pd.DataFrame:
    """Records dataframe to SQL table.

    Args:
        df: The pandas dataframe whose data will be recorded.
        table: The SQL table to be written to.
        verbose: when debugging, set to True so actual queries are printed before executed.

    Returns:
        the DataFrame of what was recorded to the SQL table.
    """

    if df.shape[0] > 0:

        df = df.copy()
        # make boolean values as 1/0 so MariaDB accepts
        for c in df.select_dtypes(['bool']).columns:
            df[c] = df[c].astype(int)

        # print(df.select_dtypes(exclude=['number']).columns)

        # wrap non-numeric values with double quotation marks so MariaDB accepts
        for c in df.select_dtypes(exclude=['number']).columns:
            df[c] = df[c].astype(str).str.replace("'", '"'
                                                 ).apply(lambda _: f"'{_}'")

        # fill `None` and `nan` with `null`s so MariaDB accepts
        df = df.fillna('null').replace(["'None'", "'nan'"], 'null')

        with engine.connect() as con:

            # read table for column names
            df_table = pd.read_sql(
                text(f'select * from {table} limit 1'), con=con
            )

            cols_common = list(df_table.columns.intersection(df.columns))
            # print(cols_common)

            # insert or update for each row in the dataframe using a batch command to transfer all records at once.
            # Setup insert fields
            query = f"""
                insert into {table}
                    ({', '.join(cols_common)})
                values
            """

            # Add values for each record
            for _, row in df.iterrows():
                query += f"""
                    ({', '.join([f'{row[c]}' for c in cols_common])}),
                """

            # remove trailing ,
            query = query.rstrip().rstrip(',')

            # On duplicate key, update instead. This includes the key columns but that's fine.
            # Uses VALUES(key) to get the value form the related values item.
            query += f"""
                on duplicate key update {', '.join([f'{c}=VALUES({c})' for c in cols_common])}
            """

            print(
                f'Writing/Updating {df.shape[0]} records ({round(len(query) / 1024 / 1024, 2)} mb) '
                f'to {table=} on columns: {cols_common}'
            )

            if verbose:
                print(query)

        with engine.begin() as con:
            con.execute(text(query))

    else:
        print(f'Skipped recording to {table=} because of empty dataframe.')

    return df

