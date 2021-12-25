from numpy.core.fromnumeric import shape
from tensorflow.python.platform.tf_logging import error
import yfinance as yf
import pandas
import datetime 
import time
import numpy
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import statistics
import matplotlib.pyplot as plt
import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from numpy import average, multiply
from tensorflow import keras

model5 = keras.models.load_model('model5Step')
model10 = keras.models.load_model('model10Step')

def movingAvg(df,period):
    movingList = []

    for i in range(dataLen-1-period*24, dataLen-1):
        movingList.append(df.loc[i, "Close"])
    MAvg = average(movingList)
    return MAvg

def rsi(df, period, interval):
    rsiList = []

    index = period*24

    for i in range(dataLen-2-int(index), dataLen-1):
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

    for i in range(dataLen-2-period*24, dataLen-2):
        if i % interval == 0 or i == 0:
            sma.append(df.loc[i, "Close"])

    sma = average(sma)
    current = df.loc[dataLen-1, "Close"]


    smooth = 2/(period+1)
    ema = current*smooth
    ema = ema + sma*(1-smooth)
    return ema

def liveDataCreation(step):
    inputData = []
    for i in range(0, step):
        print(i)
        dataLen = len(data.index)
        dataLen = dataLen - step + i
        formattedDataRow = []

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

        formattedDataRow.append(data.loc[dataLen, "Open"]/68610.171875)
        formattedDataRow.append(data.loc[dataLen, "High"]/68789.625000)
        formattedDataRow.append(data.loc[dataLen, "Low"]/68475.140625)
        formattedDataRow.append(data.loc[dataLen, "Close"]/68622.632812)
        formattedDataRow.append(data.loc[dataLen, "Adj Close"]/68622.632812)

        formattedDataRow.append(sma1/67602.707682)
        formattedDataRow.append(sma3/66756.813531)
        formattedDataRow.append(sma7/65442.836821)
        formattedDataRow.append(sma14/63944.620850)
        formattedDataRow.append(sma21/63009.884680)

        formattedDataRow.append(rsi1/95.181635)
        formattedDataRow.append(rsi3/84.039990)
        formattedDataRow.append(rsi7/76.066828)
        formattedDataRow.append(rsi14/66.344309)
        formattedDataRow.append(rsi21/62.134982)


        formattedDataRow.append(ema1/68622.632812)
        formattedDataRow.append(ema3/67478.050239)
        formattedDataRow.append(ema7/65572.406250)
        formattedDataRow.append(ema14/64073.624882)
        formattedDataRow.append(ema21/63224.333701)

        inputData.append(formattedDataRow)

    inputData = numpy.array(inputData)
    inputData = inputData.reshape(-1, step, 20)
    
    return inputData


while True:
    min = str(datetime.datetime.now())[14:16]
    time.sleep(5)

    if int(min) == 0:
        try:
            now = datetime.datetime.now()
            start = datetime.timedelta(days = 60)
            start = now - start
            start = str(start)[:10]

            data = yf.download("BTC-USD", start=start, interval="1h")
            data = data.reset_index()
            dataLen = len(data.index)

            print(data)

            inputData5 = liveDataCreation(5)
            inputData10 = liveDataCreation(10)

            pred5 = model5.predict(inputData5)*68622.632812
            pred10 = model10.predict(inputData10)*68622.632812

            hour = str(datetime.datetime.now())[11:13]

            row = []
            row.append(hour)
            row.append(data.loc[dataLen-1, "Close"])
            row.append(pred5[0,0])
            row.append(pred10[0,0])

            finalRow = []
            finalRow.append(row)
            print(pred5.shape)

            dryRun = pandas.DataFrame(finalRow, columns=["hour","close", "pred5", "pred10"])

            dryRun.to_csv('dryRun.csv', mode='a', header=False, columns=["hour","close", "pred5", "pred10"], index=False)

            time.sleep(60)
        except Exception as e:
            print("something went wrong at" + datetime.datetime.now)
            print(e)