# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#转换tushare数据到yahoo数据格式的csv文件

#==============================================================================
# yt=ts.get_hist_data('600066')
# yt.to_csv('../data/600066.csv')
# import data_utf8 as d8
# d8.change_code_type_to_yahoo('600066')
#==============================================================================


from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade import plotter
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.stratanalyzer import trades

class SMACrossOver(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod):
        strategy.BacktestingStrategy.__init__(self, feed,cash_or_brk=100000)
        self.__instrument = instrument
        self.__position = None
        # We'll use adjusted close values instead of regular close values.
        self.setUseAdjustedValues(False)
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__sma = ma.SMA(self.__prices, smaPeriod)
        self.__total_position=0
        self.__avg_price=0
        self.__buy_flag=False
        
        
          
    def getSMA(self):
        return self.__sma
    
    def onEnterCanceled(self, position):
        pass

    def onExitOk(self, position):
        self.__total_position-=position.getShares()
        
    def onEnterOk(self,position):
        self.__total_position+=position.getShares()
        if self.getBroker().getShares(self.__instrument)>0:
            self.__avg_price=(self.__position.getEntryOrder().getAvgFillPrice()*self.__position.getShares()+self.__avg_price*(self.getBroker().getShares(self.__instrument)-self.__position.getShares()))/self.__total_position
        else:
            self.__avg_price=0
        print self.__avg_price
#==============================================================================
#         print self.__position.getShares()
#         print self.getBroker().getCash()
#         print self.getBroker().getShares(self.__instrument)
#         print self.__position.getEntryOrder().getAvgFillPrice()
#         print (self.__position.getEntryOrder().getAvgFillPrice()*self.__position.getShares()+self.__avg_price*(self.getBroker().getShares(self.__instrument)-self.__position.getShares()))/self.getBroker().getShares(self.__instrument)
#==============================================================================
#        self.__position=self.getBroker().getPositions()
        

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
#        self.__position.exitMarket()
        pass

    def onBars(self, bars):
        # If a position was not opened, check if we should enter a long position.
        
        if self.getBroker().getShares(self.__instrument)==0:
            if cross.cross_above(self.__prices, self.__sma) > 0:
#                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                shares=1000
                # Enter a buy market order. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, shares, True)
                self.__avg_price=bars[self.__instrument].getPrice()
                print 'init:  buy 1000    price:'+str(bars[self.__instrument].getPrice())
#                self.__position = self.enterLong(self.__instrument, 1000, True)
#                order_cs=self.__position.getEntryOrder()
#                cs=self.__position.getReturn()
#                print self.getBroker()
        # Check if we have to exit the position.
#==============================================================================
#         elif not self.__position.exitActive() and cross.cross_below(self.__prices, self.__sma) > 0:
# #            if self.__prices<cs*0.92:
#                 print ("%s,%s" % (self.__position.getEntryOrder().getAvgFillPrice(), bars[self.__instrument].getPrice()))
#                 
#                 self.__position.exitMarket()
#==============================================================================
        elif self.getBroker().getShares(self.__instrument)>1000 and self.__avg_price<bars[self.__instrument].getPrice() and self.__buy_flag:
            self.__position=self.enterShort(self.__instrument,self.getBroker().getShares(self.__instrument)/2,True)
            self.__buy_flag=False
            print 'party sells:'+str(-1*self.getBroker().getShares(self.__instrument))+'   avg_price:'+str(self.__avg_price)+'   current price:'+str(bars[self.__instrument].getPrice())
        elif self.getBroker().getShares(self.__instrument)>0 and self.__avg_price*0.92>bars[self.__instrument].getPrice() and self.getBroker().getShares('south_air')*bars[self.__instrument].getPrice()<self.getBroker().getCash():
             self.__position=self.enterLong(self.__instrument, self.getBroker().getShares(self.__instrument), True)
             self.__buy_flag=True
             print 'add buy:'+str(self.getBroker().getShares(self.__instrument))+'   avg_price:'+str(self.__avg_price)+'   current price:'+str(bars[self.__instrument].getPrice())
        elif self.getBroker().getShares(self.__instrument)>0 and (self.__avg_price*0.92>bars[self.__instrument].getPrice() or self.__avg_price*1.2<bars[self.__instrument].getPrice()):
            #print 'loss now price:'+str(bars[self.__instrument].getPrice())
            print 'sells:'+str(-1*self.getBroker().getShares(self.__instrument))+'   avg_price:'+str(self.__avg_price)+'   current price:'+str(bars[self.__instrument].getPrice())
            #self.getBroker().createMarketOrder(broker.Order.Action.SELL, self.__instrument, self.__total_position, False)
            #self.marketOrder(self.__instrument,-1*int(self.getBroker().getShares(self.__instrument)),True,True)
            self.__position=self.enterShort(self.__instrument,self.getBroker().getShares(self.__instrument),True)
            print self.__total_position



feed = yahoofeed.Feed()
feed.addBarsFromCSV("south_air", "../data_yahoo/600066.csv")

# Evaluate the strategy with the feed's bars.
myStrategy = SMACrossOver(feed, "south_air", 20)

# Attach a returns analyzers to the strategy.
#==============================================================================
# returnsAnalyzer = returns.Returns()
# myStrategy.attachAnalyzer(returnsAnalyzer)
#==============================================================================





retAnalyzer = returns.Returns()
myStrategy.attachAnalyzer(retAnalyzer)
sharpeRatioAnalyzer = sharpe.SharpeRatio()
myStrategy.attachAnalyzer(sharpeRatioAnalyzer)
drawDownAnalyzer = drawdown.DrawDown()
myStrategy.attachAnalyzer(drawDownAnalyzer)
tradesAnalyzer = trades.Trades()
myStrategy.attachAnalyzer(tradesAnalyzer)


# Attach the plotter to the strategy.
plt = plotter.StrategyPlotter(myStrategy)
# Include the SMA in the instrument's subplot to get it displayed along with the closing prices.
plt.getInstrumentSubplot("south_air").addDataSeries("SMA", myStrategy.getSMA())
# Plot the simple returns on each bar.
plt.getOrCreateSubplot("returns").addDataSeries("Simple returns", retAnalyzer.getReturns())



# Run the strategy.
myStrategy.run()
#myStrategy.info("Final portfolio value: $%.2f" % myStrategy.getResult())

# Plot the strategy.
plt.plot()



print("Final portfolio value: $%.2f" % myStrategy.getResult())
#print("Cumulative returns: %.2f %%" % (retAnalyzer.getCumulativeReturns()[-1] * 100))
#print("Sharpe ratio: %.2f" % (sharpeRatioAnalyzer.getSharpeRatio(0.05)))
print("Max. drawdown: %.2f %%" % (drawDownAnalyzer.getMaxDrawDown() * 100))
print("Longest drawdown duration: %s" % (drawDownAnalyzer.getLongestDrawDownDuration()))

print()
print("Total trades: %d" % (tradesAnalyzer.getCount()))
if tradesAnalyzer.getCount() > 0:
    profits = tradesAnalyzer.getAll()
    print("Avg. profit: $%2.f" % (profits.mean()))
    print("Profits std. dev.: $%2.f" % (profits.std()))
    print("Max. profit: $%2.f" % (profits.max()))
    print("Min. profit: $%2.f" % (profits.min()))
    returns = tradesAnalyzer.getAllReturns()
    print("Avg. return: %2.f %%" % (returns.mean() * 100))
    print("Returns std. dev.: %2.f %%" % (returns.std() * 100))
    print("Max. return: %2.f %%" % (returns.max() * 100))
    print("Min. return: %2.f %%" % (returns.min() * 100))

print()
print("Profitable trades: %d" % (tradesAnalyzer.getProfitableCount()))
if tradesAnalyzer.getProfitableCount() > 0:
    profits = tradesAnalyzer.getProfits()
    print("Avg. profit: $%2.f" % (profits.mean()))
    print("Profits std. dev.: $%2.f" % (profits.std()))
    print("Max. profit: $%2.f" % (profits.max()))
    print("Min. profit: $%2.f" % (profits.min()))
    returns = tradesAnalyzer.getPositiveReturns()
    print("Avg. return: %2.f %%" % (returns.mean() * 100))
    print("Returns std. dev.: %2.f %%" % (returns.std() * 100))
    print("Max. return: %2.f %%" % (returns.max() * 100))
    print("Min. return: %2.f %%" % (returns.min() * 100))

print()
print("Unprofitable trades: %d" % (tradesAnalyzer.getUnprofitableCount()))
if tradesAnalyzer.getUnprofitableCount() > 0:
    losses = tradesAnalyzer.getLosses()
    print("Avg. loss: $%2.f" % (losses.mean()))
    print("Losses std. dev.: $%2.f" % (losses.std()))
    print("Max. loss: $%2.f" % (losses.min()))
    print("Min. loss: $%2.f" % (losses.max()))
    returns = tradesAnalyzer.getNegativeReturns()
    print("Avg. return: %2.f %%" % (returns.mean() * 100))
    print("Returns std. dev.: %2.f %%" % (returns.std() * 100))
    print("Max. return: %2.f %%" % (returns.max() * 100))
    print("Min. return: %2.f %%" % (returns.min() * 100))

