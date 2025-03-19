# Setup

### Prerequisites

Make sure you have the following installed on your machine:

- [Python](https://www.python.org/downloads/) (3.x)
- [pip](https://pip.pypa.io/en/stable/)

## Step 1: Clone the Repository

First, clone the repository to your local machine:

```bash
git clone <repository-url>
cd simons
```

## Step 2: Set Up a Virtual Environment

### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### On Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

The terminal prompt should change to indicate that you are in the virtual environment.

## Step 3: Install the Dependencies

With the virtual environment activated, install the required Python packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Step 4: Run the Project
```
python manage.py migrate
python manage.py runserver
```

## Step 5: Test Web UI
Navigate to http://127.0.0.1:8000/nucleotide/search/?pattern=(AATCGA|GGCAT)
and replace (AATCGA|GGCAT) as desired. To paginate through results, click the
"next" and "previous" links

## Step 6: Test management command
From the simons/ directory, run the following command, replacing the sequence id
and pattern as desired:
```
python manage.py cli_search 224589800 AATCGA
```

## Step 7: Run Tests
From the nucleotide/ directory, run the following command:
```
python -m unittest discover tests/
```

# Notes
I wasted a lot of time experimenting with chunking, buffering, range-based fetching, streaming, and concurrency (via
ThreadPoolExecutor and asyncio) to fetch and process the larger 224589800 sequence. The
goal was to break down the large sequence retrieval into smaller, manageable
parts since doing the search with the whole sequence in memory is not feasible.
I initially forgot to change the nucleotide id in the management command and
thus was underestimating exactly how big 224589800 was, which makes even
processing in chunks a challenge. I also forgot to give multiprocessing a try,
which may have been a better approach.

While using ThreadPoolExecutor and asyncio seemed
promising, I ran into challenges with rate-limiting (HTTP 429 errors). Despite
introducing sleep intervals and retry mechanisms, the overhead of managing
multiple concurrent requests also often led to slower performance (I benchmarked various versions of the nucleotide fetch function). After extensive troubleshooting, I realized that the real bottleneck was not in the fetching mechanism itself but in how I was managing
the storage and pattern searching of the large sequence. I then opted to
download the nucleotide specified in the cli command to a file for simplicity
(and to finish part 2 in time).

For a real project I'm sure I would have created a nucleotide model and stored in
Postgres in order to utilize full text search (or Postgres + Elasticsearch) I also would have likely used
Celery in order to handle the larger sequence retrieval and processing in the
background to avoid rate limiting issues via automatic retries and
exponential backoff, but I'm sure I would also have an API key in order to avoid
the public API's 3 second rate limit. In order to benefit from this
in part 1 however, I probably would have had to move away from the simplicity of
the DRF API ui in order to notify the user that a nucleotide was ready for
searching (although Celery's Flower could be use for tracking in a pinch). I
also wanted to do a simple visual representation of where the individual pattern
results occured in the sequence, but I didn't get to it. If users frequently search for the same pattern in the same nucleotide, I would also consider caching the results.

## Package decisions
* DRF for the simplicity of the built-in API UI, including pagination
* tqdm for to make up for the long download times of the large sequence without
  any user feedback

