# Back Tester
In ~2020, I developed a back tester to test strategies before I deployed them live using Alpaca. I decided to share what did to support the community that spported me throughout my algo trading journey.

The back tester uses polygon.io for historical data.

You can change the stragety. Right now it uses EMA and Candle Stick Patterns.
I found a lot of success with EMA, but when I incoprated a realestic delay (the time it takes to submit an order to the time it takes to actaully buy/sell the stock), it becomes not consistently profitable. 

Hope you find this repo useful and best of luck!
