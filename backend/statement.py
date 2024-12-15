from docx import Document
import pandas as pd
from recommend import FinancialAnalyzer  as fa
import copy

def extract(df,date,debit,credit,balance):
    li = []
    for i in df[balance]:
        li.append(float(i.replace(',','')))
    df[balance] = li

    li = []
    for i in df[date]:
        dic = {'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun','07':'Jul','08':'Aug','09':'Sep','10':'Oct','11':'Nov','12':'Dec'}
        val = i.replace('\n',' ')
        val = val.replace('-',' ')
        val = val.replace('/',' ')
        val = val.strip()
        mon = val.split(' ')
        if mon[1] in dic:
            mon[1] = dic[mon[1]]
            if len(mon[2]) == 2:
                mon[2] = '20'+mon[2]
        val = ' '.join(mon)
        li.append(val)
    df[date] = li
    
    li = []
    for i in df[debit]:
        if i == '':
            li.append(0)
        else:
            li.append(float(i.replace(',','')))
    df[debit] = li

    li = []
    for i in df[credit]:
        if i == '':
            li.append(0)
        else:
            li.append(float(i.replace(',','')))
    df[credit] = li
    return pd.DataFrame({'Date':df[date],'Debit':df[debit],'Credit':df[credit],'Balance':df[balance]})

# Function to read tables and convert to a combined DataFrame
def read_and_concat_tables(file_path,  bank):
    # Load the document
    doc = Document(file_path)
    all_tables = []
    for table in doc.tables:
        # Extract each row in the table as a list of cell text
        table_data = []
        for row in table.rows:
            row_data = [cell.text for cell in row.cells]
            table_data.append(row_data)

        # Convert table data to a DataFrame
        df = pd.DataFrame(table_data)

        # Reset the header and ensure columns are consistent
        df.columns = [f"Column {i+1}" for i in range(len(df.columns))]  # Rename columns
        df = df[1:]  # Skip the header row in the data, if applicable

        # Append each table's DataFrame to the list
        all_tables.append(df)

    # Concatenate all DataFrames into a single DataFrame
    combined_df = pd.concat(all_tables, ignore_index=True)
    ob = fa()
    # Display the combined DataFrame
    if bank == 'sbi':
        val = extract(combined_df,'Column 1','Column 5','Column 6','Column 7')
        chart_data = copy.deepcopy(val)
        analysis = ob.analyse(val)
        return [chart_data, analysis]

    elif bank == 'canara':
        val = extract(pd.DataFrame(combined_df[10:]),'Column 2','Column 6','Column 7','Column 8')
        chart_data = copy.deepcopy(val)
        analysis = ob.analyse(val)
        return [chart_data, analysis]

    elif bank == 'axis':
        val = extract(pd.DataFrame(combined_df[1:len(combined_df['Column 1'])-2]),'Column 1','Column 4','Column 5','Column 6')
        chart_data = copy.deepcopy(val)
        analysis = ob.analyse(val)
        return [chart_data, analysis]

    elif bank == 'hdfc':
        combined_df = combined_df[combined_df['Column 7'] != '']
        val = extract(pd.DataFrame(combined_df[1:len(combined_df['Column 1'])-4]),'Column 1','Column 5','Column 6','Column 7')
        chart_data = copy.deepcopy(val)
        analysis = ob.analyse(val)
        return [chart_data, analysis]
    else:
        val = extract(combined_df,'Column 1','Column 5','Column 6','Column 7')
        chart_data = copy.deepcopy(val)
        analysis = ob.analyse(val)
        return [chart_data, analysis]

