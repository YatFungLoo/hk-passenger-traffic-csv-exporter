import requests
import pandas as pd
from io import StringIO
from datetime import date, timedelta, datetime
import argparse
import os
import warnings


# URL of the CSV file
url = 'https://www.immd.gov.hk/opendata/eng/transport/immigration_clearance/statistics_on_daily_passenger_traffic.csv'


def get_args():
    parser = argparse.ArgumentParser("HK Passenger Traffic Grapher")
    today = date.today()
    parser.add_argument("--date", type=str, default=today,
                        help="date of interest, format: dd-mm-yyyy (def: yesterday)")
    parser.add_argument("--mode", type=str, default="csv",
                        help="output Mode (def: csv)")
    parser.add_argument("--output", type=str, default="out",
                        help="output name (def: out)")
    args = parser.parse_args()
    return args


def download2df():
    response = requests.get(url)
    if response.status_code == 200:
        content = response.content.decode(
            'utf-8-sig')  # 'utf-8-sig' handles the BOM
        csv_data = StringIO(content)
        df = pd.read_csv(csv_data)
        df = df.drop(columns=df.columns[df.columns.str.contains('Unnamed')])
        return df
    else:
        print(
            f"Failed to download the file. Status code: {response.status_code}")


def getDateData(df, date):
    df['Date'] = pd.to_datetime(
        df['Date'], format='%d-%m-%Y')  # convert format
    filtered_df = df[df['Date'] == pd.to_datetime(date, format='%d-%m-%Y')]
    return filtered_df


def getArrivalData(df):
    filtered_df = df[df['Arrival / Departure'] == 'Arrival']
    filtered_df = filtered_df.drop(columns=['Arrival / Departure'])
    return filtered_df


def getDepartureData(df):
    filtered_df = df[df['Arrival / Departure'] == 'Departure']
    filtered_df = filtered_df.drop(columns=['Arrival / Departure'])
    return filtered_df


def getConcatData(arrival_df, departure_df):
    column_indices = [2, 3, 4, 5]
    arrival_name = ['Arrival Hong Kong Residents',
                    'Arrival Mainland Visitors', 'Arrival Other Visitors', 'Arrival Total']
    departure_name = ['Departure Hong Kong Residents',
                      'Departure Mainland Visitors', 'Departure Other Visitors', 'Departure Total']
    old_names = arrival_df.columns[column_indices]
    arrival_df.rename(columns=dict(zip(old_names, arrival_name)), inplace=True)
    departure_df.rename(columns=dict(
        zip(old_names, departure_name)), inplace=True)
    concat_df = pd.merge(arrival_df, departure_df, on=[
                         'Date', 'Control Point'], how='outer')
    return concat_df


def output2csv(concat_df):
    output_dir = 'data'
    output_file = opt.output + '.csv'

    if not os.path.exists(output_dir):  # Create the directory
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, output_file)  # Create full path
    concat_df.to_csv(output_path, index=False)


def flaskOutput(date_input):
    try:
        date_obj = datetime.strptime(date_input, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d-%m-%Y')
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD.", 400
    
    date_df = getDateData(download2df(), formatted_date)
    concat_df = getConcatData(getArrivalData(
        date_df), getDepartureData(date_df))
    return concat_df


def main(opt):
    if opt.date == date.today():
        warnings.warn(
            "Newest available data is from yesterday, using newest data available.")
        date_df = getDateData(download2df(), opt.date - timedelta(days=2))
    else:
        date_df = getDateData(download2df(), opt.date)
    concat_df = getConcatData(getArrivalData(
        date_df), getDepartureData(date_df))

    match opt.mode:
        case 'csv':
            output2csv(concat_df)
        case 'excel':
            raise Exception('Export to excel is work in progress')


if __name__ == "__main__":
    opt = get_args()
    main(opt)
