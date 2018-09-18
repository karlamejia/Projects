# Import libraries
import csv
import pandas as pd
import numpy as np
import time
from pytrends.request import TrendReq

# Function returns top queries for given inputs
def getRelatedQueries(keywords, interval, country_id):
    """ Returns top queries for given inputs
    Parameters:
        keywords: list of keywords
        interval: interval with format %Y-%m-%d
        country_id: country ID
    """
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=keywords, timeframe=interval, geo=country_id)
    queries = pytrend.related_queries()
    queries2 = pd.DataFrame()
    for key in queries.keys():
        queries2 = pd.concat([queries2, queries[key]['top']])
    return list(queries2['query'].unique())

        
# Function returns interest-over-time data for given inputs
def getTrendsQuery(keywords, intervals, country_id):
    """ Return interest-over time data for given inputs 
    Parameters: 
        keywords: list of terms
        intervals: list of intervals with format %Y-%m-%d
        country_id: ID of country
    """
    # Initialize
    trends = pd.DataFrame()
    pytrend = TrendReq()
    # Query trends for each interval, calculate ratio between overlapping dates, use ratio 
    # to adjust trends and then concatenate adjusted trends 
    for i in range(len(intervals)):
        pytrend.build_payload(kw_list=keywords, timeframe=intervals[i], geo=country_id)
        if i==0:
            trends = pd.concat([trends, pytrend.interest_over_time()])
            if len(trends>0):
                trends = trends.drop('isPartial', axis=1)
        else:
            trends_unadj = pytrend.interest_over_time()
            trends_unadj = trends_unadj.drop('isPartial', axis=1)
            if len(trends_unadj)>0:
                ratios = trends.iloc[-1].div(trends_unadj.iloc[0])
                trends_adj = ratios*trends_unadj
                trends = pd.concat([trends, trends_adj.drop(trends_adj.index[0])])
    return trends

def getTrends(terms, intervals, country_id):
    """ Import trends for terms 
    Parameters: 
        terms: list of related terms
        interval: list of intervals in format %Y-%m-%d
        country_id: country ID
    """
    # Get interest-over-time data for 5 keywords at a time 
    trends = pd.DataFrame()
    div = 5
    if len(terms) <= div:
        trends = getTrendsQuery(terms, intervals, country_id)
        trends.reset_index(level=0, inplace=True)
    else:
        for i in range(len(terms)): 
            if i>0 and i%div==0: 
                trends = pd.concat([trends, getTrendsQuery(terms[i-div:i], intervals, country_id)], axis=1)
                time.sleep(5)
            if i>=div*np.floor(len(terms)/div)+1:
                trends = pd.concat([trends, getTrendsQuery([terms[i]], intervals, country_id)], axis=1)
                time.sleep(5)
        # Rescale trends
        trends = 100*trends/trends.max()
    # Drop columns for keywords with NAs and return data
    trends = trends.dropna(axis='columns')
    return trends

