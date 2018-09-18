# Scraping Google Trends Website
I used the [pytrends](https://github.com/GeneralMills/pytrends) package by [GeneralMills](https://github.com/GeneralMills) to write [Python](https://www.python.org/) code to scrape the [Google Trends](https://trends.google.com/trends/) website. 

The `getRelatedQueries` method allows you to get the top related queries for one or more search terms, and the `getTrends` method allows you to get the relative search frequencies for one or more search terms. Here are some simple examples of how to use `getRelatedQueries` and `getTrends`:

```python
from google_trends import *

getRelatedQueries(keywords = ['wrestlemania'], 
                  interval = '2016-01-01 2018-01-01', 
                  country_id = 'US')
                  
getTrends(keywords = ['beyonce', 'jay z'], 
          intervals = ['2010-01-01 2014-01-10', '2014-01-05 2018-01-01'], 
          'US')
```
