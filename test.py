#!/usr/bin/env python3

import sys
import xlrd

filename = sys.argv[1]
workbook = xlrd.open_workbook(filename)
sheet = workbook.sheet_by_index(0)
nrows = sheet.nrows - 1
keys = sheet.row_values(0)
values = sheet.row_values(1)

print(keys)
print(values)
