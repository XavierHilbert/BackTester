# Back Tester
In ~2020, I developed a back tester to test strategies before I deployed them live using Alpaca. I decided to share what I did to support the community that supported me throughout my algo trading journey.

The back tester uses polygon.io for historical data.

You can change the strategy. Right now it uses EMA and Candlestick Patterns. I found a lot of success with EMA, but when I incorporated a realistic delay (the time it takes to submit an order to the time it takes to actually buy/sell the stock), it becomes not consistently profitable.

Hope you find this repo useful and best of luck!

