# journey2dayone
Python script to convert a [Journey](https://journey.cloud) database of diary entries to the JSON Zip archive format for [Day One](https://dayoneapp.com). 

### Supported features
This script allows the following data from Journey to be migrated over to Day One:

* Entry text
* Date and time (including time zone)
* All images (which will be placed at the bottom of the journal entry)
* Location data (place name, latitude and longtitude)
* Weather data (temperature and description)
* Tags

### Usage
1. Export your data from `Journey.app` as a ZIP archive by following [these instructions](https://help.journey.cloud/en/article/archive-journal-entries-to-zip-format-v6dsvi/).

2. Extract the ZIP archive to a folder named `journey`, and place it in the same location as the `journey2dayonejson.py` script from this repo.

3. Run `python journey2dayonejson.py` in a terminal window, which will create a ZIP archive called `dayone.zip`.

4. Open `Day One.app` and import the JSON Zip file by following [these instructions](https://help.dayoneapp.com/en/articles/1694437-importing-data-to-day-one). This will create a new journal within `DayOne.app` called `Journey`.

5. Continue adding to your journal in `Day One.app`!
