import urllib3
import sys
import datetime
import locale
import re
import datetime
import mojimoji
import csv
import sqlite3
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

url = "http://www2.pref.iwate.jp/~hp0802/oshirase/kou-sidou/torishimari/torishimari.pdf"
now = datetime.datetime.now()
month = now.month
day = now.day
pre_line = ""
pre_filter_time = ""
rsrcmgr = PDFResourceManager()
rettxt = StringIO()
laparams = LAParams()
request_methods = urllib3.PoolManager()
response = request_methods.request('GET', url)
'''
fp = open('torishimari.pdf', 'wb')
fp.write(response.data)
fp.close()
'''
# 縦書き文字を横並びで出力する
laparams.detect_vertical = True
device = TextConverter(rsrcmgr, rettxt, codec='utf-8', laparams=laparams)

# 処理するPDFを開く
fp = open('torishimari.pdf', 'rb')
interpreter = PDFPageInterpreter(rsrcmgr, device)

# maxpages：ページ指定（0は全ページ）
for page in PDFPage.get_pages(fp, pagenos=None, maxpages=0, password=None,caching=True, check_extractable=True):
    interpreter.process_page(page)
    sentence = rettxt.getvalue()

#print (sentence)

file = open('pdf.txt', 'w')
file.write(sentence)

fp.close()
device.close()
rettxt.close()
file.close()

fp = open('pdf.txt')
lines = fp.readlines() # 1行毎にファイル終端まで全て読む(改行文字も含まれる)
fp.close()

fp = open('result.txt', 'w')
# lines: リスト。要素は1行の文字列データ
for line in lines:
    #Check date nad daytime or nigth
    if re.search('(\d{1,2})月(\d{1,2})日',line) is not None:
        date = re.search('(\d{1,2})月(\d{1,2})日',line)
        pdf_month = mojimoji.zen_to_han(date.group(1))
        pdf_day = mojimoji.zen_to_han(date.group(2))
        pdf_month = int(pdf_month)
        pdf_day = int(pdf_day)
        if pdf_month == month and pdf_day == day:
            today_flag = 1
        else:
            today_flag = 0
    if line.find("日中") > 0:
        filter_time = "日中\n"
    elif line.find("夜間") > 0:
        filter_time = "夜間\n"

    #Extract trafic crackdown
    if (line.find("盛岡") > 0 or line.find("滝沢") > 0) and today_flag == 1:
        if(pre_line != line):
            if pre_filter_time != filter_time:
                fp.write(filter_time)
                pre_filter_time = filter_time
            fp.write(line.strip())
            fp.write("\n")
            pre_line = line
fp.close()

crack_lines = open("crackdown_statistics.csv", "r", encoding="utf_8", errors="", newline="" )
break_flag = 0

for line in lines:
    crack_write = open("crackdown_statistics.csv", "w", encoding="utf_8", errors="", newline="" )
    writer = csv.writer(crack_write)
    for crack_line in crack_lines:
        if line == crack_line[0]:
            crack_line[1] += 1
            break_flag = 1
            break
    if break_flag == 1:
        writer.writerow([crack_line[0],crack_line[1]])
    else:
        line = line.strip()
        writer.writerow([line,1])
    break_flag = 0
    crack_write.close()

crack_lines.close()
