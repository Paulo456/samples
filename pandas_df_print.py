def print_df(dataframe):
    list_columns = list(dataframe.columns)
    list_columns.sort()
    df_text=''
    for column in list_columns:
        df_text += str(column) + ';\t'
    df_text += '\n'
    for row in range(len(dataframe)):
        for column in list_columns:
            df_text += str(dataframe.loc[row,column]) + ';\t'
        df_text += '\n'
    return df_text
