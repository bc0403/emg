# Created by Hao Jin on 2020/06/20.
# Copyright (c) 2020 Hao Jin. All rights reserved.

"""
convert one line data format to dataframe format

32 columns (32 channels)
n rows (one timestamp one row)
"""

datafile = "1-1.txt"
output = "1-1_df.csv"

with open(datafile, 'r') as f:
    v = f.readline().split(" ")

with open(output, 'w') as f:
    for n in range(len(v)//32):
        f.write(' '.join(v[n*32:(n+1)*32]) + "\n")
