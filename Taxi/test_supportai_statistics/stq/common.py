def dataframe_to_table(dataframe):
    columns = list(dataframe.columns)
    table = []
    df_content = dataframe.to_dict('records')
    for record in df_content:
        table.append([record.get(column) for column in columns])
    return table
