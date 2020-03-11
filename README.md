# goodreads_grapher
Rating Graphs for your GoodReads Authors and Series

```bash
goodreads_grapher -h
usage: goodreads_grapher [-h] --client-key CLIENT_KEY --client-secret
                         CLIENT_SECRET [--cut-off CUT_OFF]
                         [--prompt-more-urls] [--prompt-new-cutoff]
                         [--sort-by-rating]
                         [--min-num-ratings MIN_NUM_RATINGS]
                         (--author AUTHOR | --series SERIES)
                         urls [urls ...]

positional arguments:
  urls                  Enter as many goodreads urls as you like, must all be
                        of the same type, authors or series

optional arguments:
  -h, --help            show this help message and exit
  --client-key CLIENT_KEY
                        Goodreads client key, generate one at
                        https://www.goodreads.com/api/keys
  --client-secret CLIENT_SECRET
                        Goodreads client secret, generate one at
                        https://www.goodreads.com/api/keys
  --cut-off CUT_OFF     Define a cutoff for the graph, makes graphs more
                        compact/legible
  --prompt-more-urls    Enable interactive url mode, which prompts for more
                        URLs after generating a graph
  --prompt-new-cutoff   Enable interactive cutoff mode, which prompts for a
                        new cutoff number
  --sort-by-rating      Sort the resulting graph by the rating descending
  --min-num-ratings MIN_NUM_RATINGS
                        The minimum number of ratings needed for a book to be
                        in the graph. Onlyapplies to authors mode
  --author AUTHOR       Flag to set author mode
  --series SERIES       Flag to set series mode
```