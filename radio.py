import requests
from bs4 import BeautifulSoup
import argparse
from datetime import datetime, timezone

TILDE_RADIO_SCHEDULE_URL = "https://tilderadio.org/schedule/"
TILDE_RADIO_DATETIME_FORMAT = "%a %b %d %H:%M"
OUTPUT_DATETIME_FORMAT = "%m/%d %H:%M"

class Show:
    def __init__(self, name, start_date, end_date):
       self.name = name
       self.start_date = start_date
       self.end_date = end_date


    def is_currently_playing(self):
        return (self._is_before_current_date(self.start_date)
            and self._is_after_current_date(self.end_date))


    def is_upcoming(self):
        return self._is_after_current_date(self.start_date)
 

    def _is_before_current_date(self, date):
        current_date = datetime.now(timezone.utc)
        return (date.month <= current_date.month
            and date.day <= current_date.day
            and date.time() <= current_date.time())
    

    def _is_after_current_date(self, date):
        current_date = datetime.now(timezone.utc)
        return (date.month >= current_date.month
            and date.day >= current_date.day
            and date.time() > current_date.time())


class Schedule:
    def __init__(self):
        self.shows = self._get_shows()

    def get_currently_playing(self):
        for show in self.shows:
            if show.is_currently_playing():
                return show
        return None

    def get_next(self):
        for show in self.shows:
            if show.is_upcoming():
                return show
        return None

    def _get_shows(self):
        page = self._get_page()
        soup = BeautifulSoup(page, "html.parser")

        table = soup.find("table", attrs={ "class": "table-striped" })
        tbody = table.find("tbody")
        rows = tbody.find_all("tr")

        shows = []
        for row in rows:
            data = row.find_all("td")
            name = data[0].text
            start_date = datetime.strptime(data[1].text, TILDE_RADIO_DATETIME_FORMAT)
            end_date = datetime.strptime(data[2].text, TILDE_RADIO_DATETIME_FORMAT)
            
            show = Show(name, start_date, end_date)
            shows.append(show)
       
        return shows

    def _get_page(self):
        response = requests.get(TILDE_RADIO_SCHEDULE_URL)
        return response.text

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    #parser.add_argument('-n', type=int, default=4, help='Number of words to generate')

    #args = parser.parse_args()
    #run(args.n)
    schedule = Schedule()
    currently_playing = schedule.get_currently_playing()
    next_show = schedule.get_next()

    if currently_playing is None:
        print("Currently playing: Archive Radio\n")
    else:
        start_date = currently_playing.start_date.strftime(OUTPUT_DATETIME_FORMAT)
        end_date = currently_playing.end_date.strftime(OUTPUT_DATETIME_FORMAT)
        print(f'Currently playing: {currently_playing.name}')
        print(f'Start: {start_date}')
        print(f'End: {end_date}\n')
        
    if next_show is not None:
        start_date = next_show.start_date.strftime(OUTPUT_DATETIME_FORMAT)
        end_date = next_show.end_date.strftime(OUTPUT_DATETIME_FORMAT)
        print(f'Next: {next_show.name}')
        print(f'Start Time: {start_date}')
        print(f'End Time: {end_date}')
