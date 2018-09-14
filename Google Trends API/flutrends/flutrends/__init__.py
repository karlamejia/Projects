import csv
import datetime
import sys
import time
import os
import pandas as pd

from googleapiclient.discovery import build

# ------ Insert your API key in the string below. -------
API_KEY = '.'

SERVER = 'https://www.googleapis.com'
API_VERSION = 'v1beta'
DISCOVERY_URL_SUFFIX = '/discovery/v1/apis/trends/' + API_VERSION + '/rest'
DISCOVERY_URL = SERVER + DISCOVERY_URL_SUFFIX
MAX_QUERIES = 5
TODAY = time.strftime('%Y-%m-%d')
QTERMS = "flu"


## For switching between testing on personal computer (1) and running on server (0).
#testing = False
#if testing == True:
#    home_dir = '/Users/TaisMBP13/Desktop/Dropbox/HealthMap/Flucast_Code/New_Flucast_Code/'
#elif testing == False:
#    home_dir = '/var/www/vhosts/healthmap.org/scripts/flucast/'  


def DateToISOString(datestring):
  """Convert date from (eg) 'Jul 04 2004' to '2004-07-11'.

  Args:
    datestring: A date in the format 'Jul 11 2004', 'Jul 2004', or '2004'

  Returns:
    The same date in the format '2004-11-04'

  Raises:
     ValueError: when date doesn't match one of the three expected formats.
  """

  try:
    new_date = datetime.datetime.strptime(datestring, '%b %d %Y')
  except ValueError:
    try:
      new_date = datetime.datetime.strptime(datestring, '%b %Y')
    except ValueError:
      try:
        new_date = datetime.datetime.strptime(datestring, '%Y')
      except:
        raise ValueError("Date doesn't match any of '%b %d %Y', '%b %Y', '%Y'.")

  return new_date.strftime('%Y-%m-%d')


def exportCSV(result, fun):
    """ Export results to CSV file.
    Args:
        result: List of lists
    """
    today = time.strftime('%Y-%m-%d')
    if fun == 'getQueryVolumes':
        filename = 'GFT-' + today + '.csv'
    elif fun == 'getTopQueries':
        filename = 'TopQs-' + today + '.csv'
        
    output = pd.DataFrame()
    for i in range(1,len(result)):
        output = pd.concat([output,pd.DataFrame([result[i]])])
    output.columns = result[0]
    
    output.to_csv(filename)

def getQueryVolumes(queries, start_date, end_date, geo_id, geo_level="country", frequency="week"):
    """ Extract query volumes from Flu Trends API.
    Args:
        queries: A list of all queries to use.
        start_date: Start date for timelines, in form YYYY-MM-DD.
        end_date: End date for timelines, in form YYYY-MM-DD.
        geo_id: The code for the geography of interest which can be either country
        (eg "US"), region (eg "US-NY") or DMA (eg "501").
        geo_level: The granularity for the geo_id limitation. Can be "country", 
        "region", or "dma"
        frequency: The time resolution at which to pull queries. One of "day", 
        "week", "month", "year".

      Raises:
          ValueError: 
              when API_KEY is not set
              when geo_level is not one of "country", "region" or "dma".
    """
    if not API_KEY: 
        raise ValueError('API_KEY not set.')
    
    service = build('trends', API_VERSION,
                    developerKey=API_KEY,
                    discoveryServiceUrl=DISCOVERY_URL)
    
    # Note that the API only allows querying 30 queries in one request. In
    # the event that we want to use more queries than that, we need to break
    # our request up into batches of 30.
    batch_intervals = range(0, len(queries), MAX_QUERIES)
    
    for batch_start in batch_intervals:
        batch_end = min(batch_start + MAX_QUERIES, len(queries))
        query_batch = queries[batch_start:batch_end]

    # Make API query
    if geo_level == 'country':
        # Country format is ISO-3166-2 (2-letters), e.g. 'US'
        req = service.getTimelinesForHealth(terms=query_batch,
                                            time_startDate=start_date,
                                            time_endDate=end_date,
                                            timelineResolution=frequency,
                                            geoRestriction_country=geo_id)
    elif geo_level == 'dma':
        # See https://support.google.com/richmedia/answer/2745487
        req = service.getTimelinesForHealth(terms=query_batch,
                                            time_startDate=start_date,
                                            time_endDate=end_date,
                                            timelineResolution=frequency,
                                            geoRestriction_dma=geo_id)
    elif geo_level == 'region':
        # Region format is ISO-3166-2 (4-letters), e.g. 'US-NY' (see more examples
        #here: en.wikipedia.org/wiki/ISO_3166-2:US)
        req = service.getTimelinesForHealth(terms=query_batch,
                                            time_startDate=start_date,
                                            time_endDate=end_date,
                                            timelineResolution=frequency,
                                            geoRestriction_region=geo_id)
    else:
        raise ValueError("geo_type must be one of 'country', 'region' or 'dma'")

    res = req.execute()

    # Sleep for 1 second so as to avoid hittting rate limiting.
    time.sleep(1)

    # Convert the data from the API into a dictionary of the form
    # {(query, date): count, ...}
    res_dict = {(line[u'term'], DateToISOString(point[u'date'])):
                point[u'value']
                for line in res[u'lines']
                for point in line[u'points']}

    # Update the global results dictionary with this batch's results.
    dat = {}
    dat.update(res_dict)

    # Make the list of lists that will be the output of the function
    res = [['date'] + queries]
    for date in sorted(list(set([x[1] for x in dat]))):
        vals = [dat.get((term, date), 0) for term in queries]
        res.append([date] + vals)
    
    exportCSV(res, 'getQueryVolumes')
    
    
    
def getTopQueries(term, start_date, end_date, geo_id):
    """ Extract top queries from Flu Trends API.
    Args:
        term: A search term or query.
        start_date: Start date for top queries, in form YYYY-MM.
        end_date: End date for top queries, in form YYYY-MM.
        geo_id: The code for the geography of interest which can be either country
        (eg "US"), region (eg "US-NY") or DMA (eg "501").

      Raises:
          ValueError: 
              when API_KEY is not set
              when geo_level is not one of "country", "region" or "dma".
    """
    if not API_KEY:
        raise ValueError('API_KEY not set.')
    
    service = build('trends', API_VERSION,
                    developerKey=API_KEY,
                    discoveryServiceUrl=DISCOVERY_URL)
    
    req = service.getTopQueries(term=term,
                                        restrictions_startDate=start_date,
                                        restrictions_endDate=end_date,
                                        restrictions_geo=geo_id)
    
    res = req.execute()
    
    # Convert the data from the API into a list of lists
    res_list = [['term', 'value']]
    for item in res[u'item']:
        res_list.append([item[u'title'], item[u'value']])
    
    exportCSV(res_list, 'getTopQueries')

#def main():
#  print ('+++ START +++')
#
#  geolevel = sys.argv[1]
#  geo_id = sys.argv[2]
#
#  qterms = QTERMS.split(',')
#
#  # Examples of calling the GetQueryVolumes function for different geo
#  # levels and time resolutions.
#  # geo can be "US", "US-MA", "506"(boston) respective to geo_level below
#  # geo_level can be country, region or dma
#  # frequency can be week, day, or month
#  getcounts = GetQueryVolumes(qterms,
#                              start_date='2010-01-04',
#                              end_date=TODAY,
#                              geo=geo_id,
#                              geo_level='country',
#                              frequency='week')
#
#  # Example of writing one of these files out as a CSV file to GTdata.
#  csv_out = open(home_dir + 'uploads/GTdata.csv', 'wb')
#  outwriter = csv.writer(csv_out)
#  for row in getcounts:
#    outwriter.writerow(row)
#  csv_out.close()
#
#  print ('+++ END +++')
#
#if __name__ == '__main__':
#  main()
#
