# call this py with args
# - -csvDir <path to csv files>
# - or -csv <path to csv file>
# - -outputFile <output file name>

# this script will read the csv files and generate a summary report as json file

import argparse
import os
import json
import pandas as pd
import numpy as np

def main():
    print('Generating summary report from csv files...')

    parser = argparse.ArgumentParser(description='Generate summary report from csv files')
    parser.add_argument('-csvDir', type=str, help='path to csv files')
    parser.add_argument('-csv', type=str, help='path to csv file')
    parser.add_argument('-outputFile', type=str, help='output file name')
    parser.add_argument('-name', type=str, help='name of the test')
    args = parser.parse_args()

    csvs = []
    csvFiles = []
    too_small_size = 1024

    if args.csvDir:
        csvFiles = [f for f in os.listdir(args.csvDir) if f.endswith('.csv')]
        if len(csvFiles) == 0:
            print('No csv files found in the directory')
            return
        for f in csvFiles:
            # check if file is not empty
            if os.path.getsize(os.path.join(args.csvDir, f)) > too_small_size:
                csvs.append(pd.read_csv(os.path.join(args.csvDir, f), on_bad_lines='skip'))
    elif args.csv:
        # only append the file name
        csvFiles = [args.csv.split('/')[-1].split('\\')[-1]]
        csvs.append(pd.read_csv(args.csv, on_bad_lines='skip'))
    else:
        print('No csv file or directory provided')
        return
    
    summary = {
        'name': args.name,
        'tests': []
    }

    for i, df in enumerate(csvs):
        print('Analyzing csv file: ', i)
        summary['tests'].append(analyze_df(df, csvFiles[i]))

    if args.outputFile:
        print('Writing summary report to file: ' + args.outputFile + '...')
        with open(args.outputFile, 'w') as f:
            f.write(json.dumps(summary, indent=4))
    else:
        print("No output file provided, printing to console...")
        print(summary)



def analyze_df(df, file_name=None):
    result = {
        'name': file_name
    }

    template = {'max': 0, 'min': 0, 'avg': 0}

    gt = template.copy()
    rt = template.copy()
    frame = template.copy()
    fps_output = template.copy()

    gt['max'] = float(df['GameThreadTime'].max())
    gt['min'] = float(df['GameThreadTime'].min())
    gt['avg'] = float(df['GameThreadTime'].mean())
    rt['max'] = float(df['RenderThreadTime'].max())
    rt['min'] = float(df['RenderThreadTime'].min())
    rt['avg'] = float(df['RenderThreadTime'].mean())

    print('GT: ', gt)
    print('RT: ', rt)

    frame['max'] = float(df['FrameTime'].max())
    frame['min'] = float(df['FrameTime'].min())
    frame['avg'] = float(df['FrameTime'].mean())

    print('Frame: ', frame)

    frame_times = df['FrameTime'].values

    # analyze frame times, construct FPS array
    fps = []
    accumulated_time = 0
    frame_offset = 0
    for i in range(len(frame_times)):
        accumulated_time += frame_times[i]
        if accumulated_time >= 1000:
            fps.append(i - frame_offset)
            accumulated_time = 0
            frame_offset = i

    fps_output['max'] = float(np.max(fps))
    fps_output['min'] = float(np.min(fps))
    fps_output['avg'] = float(np.mean(fps))

    print('FPS: ', fps_output)

    result['GameThreadTime'] = gt
    result['RenderThreadTime'] = rt
    result['FrameTime'] = frame
    result['FPS'] = fps_output

    return result


if __name__ == '__main__':
    main()