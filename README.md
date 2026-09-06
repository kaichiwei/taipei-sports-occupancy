# Greater Taipei Sports Center Occupancy Aggregator
#### Video Demo:  <URL HERE>
#### Description:

A command-line tool that retrieves live occupancy data from websites of sports centers  across Greater Taipei, normalizes the data into a consistent format, and displays occupancy information for gyms, swimming pools, and ice rinks. The program also saves the retrieved data to CSV files, allowing it to accumulate historical time series.


## Features

- Fetches real-time facility occupancy data from supported sports centers
- Displays the data in a color-coded table in the terminal
- Appends occupancy data to monthly CSV log files for time-series analysis
- Supports multiple sports centers in a single query


## Requirements

- Python 3.12


## Installation

```bash
pip install -r requirements.txt
```


## Usage

Run the program with:

```bash
python project.py
```

When prompted, enter the names of the sports centers you want to check in either Chinese or English. Multiple names have to be separated by any of the following punctuation marks: `，`, `、`, `；`, `,`, `;`.

For example:
```text
選擇場館： 蘆洲、松山、土城
```


## Output
### CLI table
The table displays the current occupancy information for the selected sports centers:

- **Facility**: The facility being monitored, gym, swimming pool, or ice rink.
- **Current**: The current number of users in this facility.
- **Capacity**: The maximum number of users allowed in this facility. Displays `-` if capacity data is unavailable.
- **Occupancy**: The current occupancy rate, calculated as `(current / capacity) × 100%`. The bar is color-coded according to the occupancy rate:

        Green: below 30%
        Yellow: 30% to below 60%
        Red: 60% to below 100%
        Purple: 100% or above

    Displays `-` if capacity data is unavailable.

- **time**: The time at which the data was retrieved.
- **website**: The source website from which the data was retrieved.

For example:

<img src="docs/example-output.png" alt="Example output" width="600">


### Save to CSV
Each time the program retrieves occupancy data, the results are appended to a monthly CSV log file in the `data/` directory. The destination file is determined by the retrieval timestamp and is named using the format `log_YYYY-MM.csv`. Each facility is stored as a separate row, so a sports center with a gym, swimming pool, and ice rink produces three rows.

The CSV contains the following columns:

- `timestamp`: The time at which the data was retrieved
- `city`: The city code of the sports center
- `name_zh`: The Chinese name of the sports center
- `name_en`: The English name of the sports center
- `facility`: The facility type, such as gym, pool, or rink
- `current`: The current number of users 
- `capacity`: The maximum capacity; left blank if unavailable

```csv
timestamp,city,name_zh,name_en,facility,current,capacity
2026-09-05 17:31:14,NTPC,蘆洲,Luzhou,gym,63,
2026-09-05 17:31:14,NTPC,蘆洲,Luzhou,pool,75,
2026-09-05 17:31:15,TPE,松山,Songshan,gym,81,100
2026-09-05 17:31:15,TPE,松山,Songshan,pool,240,400
2026-09-05 17:31:16,NTPC,土城,Tucheng,gym,41,120
2026-09-05 17:31:16,NTPC,土城,Tucheng,pool,55,280
2026-09-05 17:31:16,NTPC,土城,Tucheng,rink,75,250
```


### Invalid Input
If an invalid sports center name or an unrecognized string is entered, the program reports the invalid input and displays a list of supported sports centers.

<details>
<summary>Example invalid input</summary>

```text
選擇場館： abc

找不到場館：abc

Cannot find sites: abc

可選場館：
大安、板橋、新店、蘆竹、大同、中正、淡水、泰山、楊梅、松山、萬華、蘆洲、五股、南港、中山、內湖、文山、汐止、永和、林口、桃園、中壢、八德、竹光、朝馬、北屯、信義、三峽、鶯歌、台北大學、北投、中和、新莊、樹林、三重、土城、士林、新生

Available sites:
Daan, Banqiao, Xindian, Luzhu, Datong, Zhongzheng, Tamsui, Taishan, Yangmei, Songshan, Wanhua, Luzhou, Wugu, Nangang, Zhongshan, Neihu, Wenshan, Xizhi, Yonghe, Linkou, Taoyuan, Zhongli, Bade, Zhuguang, Chaoma, Beitun, Xinyi, Sanxia, Yingge, NTPU, Beitou, Zhonghe, Xinzhuang, Shulin, Sanchong, Tucheng, Shilin, Xinsheng
```

</details>


## Project Structure

```text
taipei-sports-occupancy
├── README.md
├── data
│   ├── log_2026-08.csv
│   ├── log_2026-09.csv
│   └── sample_occupancy.csv
├── docs
│   └── example-output.png
├── project.py
├── requirements.txt
├── sites.py
└── test_project.py
```


## Files
每個檔案「負責什麼」。
### `README.md`
### `data/`:
Stores monthly occupancy log csv files.
### `docs/`: 
Stores documentation assets such as the example output image.
### `project.py`:
Contains the main program logic, including user input handling, data retrieval, parsing, table rendering, and CSV logging.
### `requirements.txt`:
Lists the project's Python dependencies.
### `sites.py`:
Stores configuration for supported sports centers, including names, located city, URLs, operators, fetch modes, and site-specific parsing information.
### `test_project.py`:
Contains tests for the testable functions in `project.py`.



## Design Decisions

### Supporting Multiple Operators and Data Sources

The project currently supports 38 sports centers across five cities and ten operators. Because these operators use different website systems and data formats, the program uses a site-specific configuration layer rather than a single hard-coded scraping method.

Site-specific information is stored separately in `sites.py`. Each sports center has its own configuration, such as its names, operator, data source, and information required to retrieve or parse its occupancy data. Separating this configuration from the main program logic makes it easier to support sites with different implementations and to add or modify sports centers without rewriting the core workflow in `project.py`.


### Input Handling

After the user input is split into individual site names, the program separates them into valid and invalid entries. Invalid entries are collected rather than causing the program to stop immediately.

This allows the program to report all unrecognized site names at once and display a list of available sports centers, making it easier for the user to correct the input. Valid site names can still be processed normally.


### Fetching Data

Sites expose their occupancy data in three main ways: JSON APIs, data embedded in HTML, and comma-separated plain text.

Different sports centers operated by the same company may use different website implementations and data formats. For example, CCE uses JSON for Zhonghe Sports Center but HTML for Beitou Sports Center; YMCA also uses JSON for Xinsheng Sports Center but HTML for Shilin Sports Center. Because of this, the program cannot determine the fetching method based on `SITES["operator"]` alone. Instead, each site's `SITES["mode"]` setting in `sites.py` specifies how its data should be retrieved.

Each site is given its own retrieval timestamp rather than sharing one timestamp across the entire query. Since sites are fetched sequentially, recording a timestamp for each fetch makes the retrieval time more accurate. Facilities returned by the same fetch, such as a gym, pool, and rink from one sports center, share the same timestamp.

 
### Normalizing and Parsing Data

After retrieval, the program may receive occupancy data as JSON, HTML, or plain text. Because these formats have different structures, they cannot be parsed in a single way. Threrefore separate parsing functions are used for the three source formats: `parse_json()`, `parse_html()`, and `parse_text()`.

Additional handling is required for HTML-based sites because their page structures are not consistent. Site-specific regular expression patterns are stored in `SITES["pattern"]` in `sites.py`. The parser can use the pattern defined for each site accordingly while keeping the parsing logic generic.

One exception among HTML-based sites is the Fullhouse-operated site. Its HTTP response is HTML, but the relevant occupancy data is embedded as JSON inside the page. The JSON data must therefore be extracted from the HTML first and then parsed.

In each parser, source-specific responses are normalized into the same `facilities` dictionary structure. This allows the rest of the program to render tables and write CSV rows without needing to know whether the original data came from JSON, HTML, or plain text.

The helper function `to_int()` converts retrieved values into integers before they are stored in `facilities`. If a value is missing or cannot be converted, it returns `None`, keeping the normalized data types consistent across different sources.


### Handling Missing Data

Not all sports centers provide a maximum capacity for their facilities. For example, Luzhou and Wugu Sports Centers operated by Chan Chao provide the current number of users but do not provide capacity data.

To handle this consistently, the values in the `facilities` dictionary are initialized as `None`. When a source does not provide a value, each parser updates only the values that are available, while unavailable fields simply remain `None`.

Missing capacity values are stored as `None` rather than `0`, because a value of `0` would represent an actual capacity of zero, while `None` means that the source does not provide the information. This distinction also prevents the program from calculating a misleading occupancy percentage when capacity data is unavailable.


### Terminal Presentation

The terminal output is rendered with Rich rather than plain `print()` statements. A Rich `Table` keeps facility names, current counts, capacities, occupancy rates, timestamps, and source URLs aligned when multiple sports centers are displayed.

Occupancy is calculated as the current number of users divided by the facility capacity. Color-coded bars are used to make different occupancy levels easier to recognize at a glance. The thresholds are presentation choices intended to distinguish low, moderate, high, and over-capacity usage.

The source website is also displayed in the table so that users can easily visit the original website and verify the occupancy data.


### CSV Logging

Each CSV row represents one facility at one sports center. Therefore, if a sports center provides a gym, swimming pool, and ice rink, one retrieval produces three rows. This structure allows sports centers with different combinations of facilities to be stored in the same CSV format.

Splitting logs by month prevents a single CSV file from growing indefinitely and makes it easier to organize and analyze historical data by time period.
