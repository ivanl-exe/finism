from sys import path
path.append(
    'api'
)

import toml
from pandas import DataFrame
from datetime import datetime
from backend.src.cryptism import *
from backend.src.cryptism import key
from backend.src.stockism import *
from backend.src.technical_analysis import *

class Finism:
    FIAT = 'USD'
    
    def __init__(self) -> None:
        self.symbols = toml.load(
            'api/backend/symbols.toml'
        )
    
    def stock_history(self):
        queue = {}
        for classification, value in self.symbols.items():
            queue[classification] = {}
            for v in value:
                name, symbol = v.split(',')
                queue[classification].update({
                    (name, symbol): {}
                })
        self.symbols = queue

        for ticker in self.symbols['stock'].keys():
            name, symbol = ticker
            stockism = Stockism(symbol)
            
            data = stockism.history(
                period.YEARS_2,
                interval.DAY
            )

            ta = TechnicalAnalysis(
                data,
                close = history.CLOSE,
                window = 20
            )

            ta.sma()
            ta.ema()
            ta.macd()
            ta.rsi()

            #data = ta.export()
            data = ta.df
            self.symbols['stock'][ticker] = data
        return self.symbols['stock']

    def crypto_ticker(self):
        for ticker in self.symbols['crypto'].keys():
            if key.PRICE not in ticker:
                self.symbols['crypto'][ticker]['price'] = {}

        for ticker in self.symbols['crypto'].keys():
            name, symbol = ticker
            cryptism = Cryptism()
            listing = cryptism.listing(
                symbol
            )
            
            local = cryptism.ticker(
                listing,
                convert = Finism.FIAT,
                keys = [
                    key.RANK,
                    key.CIRCULATING_SUPPLY,
                    key.TOTAL_SUPPLY,
                    key.PRICE,
                    key.VOLUME_24H,
                    key.MARKET_CAP,
                    key.TIMESTAMP
                ]
            )

            self.symbols['crypto'][ticker][key.PRICE].update({
                pd.to_datetime(
                    local[key.TIMESTAMP],
                    unit = 's'
                ): local[key.PRICE]
            })
        
            
            ta = TechnicalAnalysis(
                self.symbols['crypto'][ticker],
                close = key.PRICE,
                window = 5
            )

            ta.sma()
            ta.ema()
            ta.macd()
            ta.rsi()

            return ta.df
    
    def crypto_fear_and_gread(self) -> None:
        cryptism = Cryptism()
        fng = cryptism.fear_and_greed(
            limit = 0,
            keys = [
                key.VALUE,
                key.CLASSIFICATION,
                key.TIMESTAMP
            ]
        )

        data = {
            key.TIMESTAMP: [],
            key.VALUE: []
        }
        for value, classification, timestamp in zip(*fng.values()):
            time = datetime.strptime(
                timestamp,
                f'%d-%m-%Y'
            )
            data[key.TIMESTAMP].append(
                time
            )
            data[key.VALUE].append(
                value
            )
        
        return DataFrame(data)