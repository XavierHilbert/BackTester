# Back Tester
In ~2020, I developed a back tester to test strategies before I deployed them to live. I decided to share what did to support the community that spported throughout my algo trading journey.

The back tester uses polygon.io for historical data.

You can change the stragety, right now it uses EMA and Candle Stick Patterns.
I found a lot of success with EMA, but just was a warning, I found that when I incoprated a delay into backtesting (the time it takes to submit the order to the time it takes for you got actaully buy/sell the stock), it becomes not consistently profitable. 

Best of luck!
