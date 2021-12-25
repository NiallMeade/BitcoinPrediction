from numpy import average, multiply
import yfinance as yf
import pandas
import datetime 
import time

now = datetime.datetime.now()
start = datetime.timedelta(days = 729)
start = now - start
start = str(start)[:10]
print(start)

data = yf.download("BTC-USD", start="2019-12-21", interval="1h")
data = data.reset_index()
print(data)
dataLen = len(data.index)

def movingAvg(df,period):
    movingList = []

    for i in range(dataLen-2-period*24, dataLen-2):
        movingList.append(df.loc[i, "Close"])
    MAvg = average(movingList)
    return MAvg

def rsi(df, period, interval):
    rsiList = []

    index = period*24

    for i in range(dataLen-3-int(index), dataLen-2):
        if i % interval == 0 or i == 0:
            rsiList.append(df.loc[i, "Close"])
    
    up = []
    down = []

    for i in range(0,len(rsiList)-1):
        if i != 0:
            if rsiList[i] > rsiList[i-1]:
                pChange =  rsiList[i] - rsiList[i-1]
                # pChange = pChange/rsiList[i-1]
                up.append(pChange)
                down.append(0)
            if rsiList[i] < rsiList[i-1]:
                pChange =  rsiList[i-1] - rsiList[i]
                # pChange = pChange/rsiList[i-1]
                down.append(pChange)
                up.append(0)
    
    top = average(up)
    bottom = average(down)
    rs = top/bottom + 1
    rsiValue = 100 - (100/rs)

    return rsiValue

def expMa(df, period, interval):
    sma = []

    for i in range(dataLen-3-period*24, dataLen-3):
        if i % interval == 0 or i == 0:
            sma.append(df.loc[i, "Close"])

    sma = average(sma)
    current = df.loc[dataLen-2, "Close"]


    smooth = 2/(period+1)
    ema = current*smooth
    ema = ema + sma*(1-smooth)
    return ema


print(movingAvg(data,30))
print(rsi(data,2, 1))
print(expMa(data, 30, 24))
print(data.loc[dataLen-2, "index"])

formattedData = []

rounds = len(data.index)

for i in range(0, rounds-510):

    dataLen = len(data.index)
    dataLen = dataLen - i
    formattedDataRow = []
    date = str(data.loc[dataLen-2, "index"])

    sma1 = movingAvg(data, 1)
    sma3 = movingAvg(data, 3)
    sma7 = movingAvg(data, 7)
    sma14 = movingAvg(data, 14)
    sma21 = movingAvg(data, 21)

    rsi1 = rsi(data, 1, 1)
    rsi3 = rsi(data, 3, 1)
    rsi7 = rsi(data, 7, 1)
    rsi14 = rsi(data, 14, 1)
    rsi21 = rsi(data, 21, 1)

    ema1 = expMa(data, 1, 1)
    ema3 = expMa(data, 3, 1)
    ema7 = expMa(data, 7, 1)
    ema14 = expMa(data, 14, 1)
    ema21 = expMa(data, 21, 1)

    formattedDataRow.append(date)

    formattedDataRow.append(sma1)
    formattedDataRow.append(sma3)
    formattedDataRow.append(sma7)
    formattedDataRow.append(sma14)
    formattedDataRow.append(sma21)

    formattedDataRow.append(rsi1)
    formattedDataRow.append(rsi3)
    formattedDataRow.append(rsi7)
    formattedDataRow.append(rsi14)
    formattedDataRow.append(rsi21)

    formattedDataRow.append(ema1)
    formattedDataRow.append(ema3)
    formattedDataRow.append(ema7)
    formattedDataRow.append(ema14)
    formattedDataRow.append(ema21)

    formattedDataRow.append(data.loc[dataLen-1, "Close"])

    print(formattedDataRow)
    formattedData.append(formattedDataRow)
    print(datetime.datetime.now())

formattedData.reverse()
formattedData.pop()

data = data[:-2]

print(data)
print(formattedData)

print(len(data), len(formattedData))
data = data[len(data)-len(formattedData):]
data = pandas.DataFrame.drop(data, columns="Volume")

newData = pandas.DataFrame(formattedData, columns=["date", "sma1", "sma3", "sma7", "sma14", "sma21", "rsi1", "rsi3", "rsi7", "rsi14", "rsi21", "ema1", "ema3", "ema7", "ema14", "ema21", "followingClose"])

data.reset_index(drop=True, inplace=True)
newData.reset_index(drop=True, inplace=True)
print(newData)
print(data)

finalData = pandas.concat([data, newData], axis=1)
print(finalData)

finalData.to_csv("finalData.csv")

df = pandas.read_csv("finalData.csv")