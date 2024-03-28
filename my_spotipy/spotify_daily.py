from datetime import datetime, date
from my_spotipy.spotify_object import sp_obj
from app.models.charts import daily_tracks, daily_artists

def JSON_to_listofDicts(
        daily_results_JSON,
        model,
        ):
    '''
    Parses a JSON that is delivered from either of the two daily type API requests made
    Use *(table_name, raw_JSON) to unpack the tuple from spot_funcs.daily_table
    '''
    hit_list = []
    position = 1


    if model == daily_artists:

        for i in daily_results_JSON['items']:
            hit_record = {}
            hit_record['position'] = position
            #on 13FEB2024, the .id field from the top_artists API endpoint was returning all the same art_id
            hit_record['art_id'] = i['uri'][-22:]
            hit_record['art_name'] = i['name']
            #hit_record['date'] = datetime.now().strftime("%Y-%m-%d")
            hit_record['date'] = datetime.now().date()
            
            position += 1
            hit_list.append(hit_record)
    
    if model == daily_tracks:

        for i in daily_results_JSON['items']:
            hit_record = {}
            hit_record['position'] = position
            hit_record['art_id'] = i['artists'][0]['id']
            hit_record['art_name'] = i['artists'][0]['name']
            hit_record['album_name'] = i['album']['name']
            hit_record['song_id'] = i['external_urls']['spotify'][-22:]
            hit_record['song_name'] = i['name']
            hit_record['date'] = datetime.now().date()
            #hit_record['date'] = datetime.now().strftime("%Y-%m-%d")
    
            position += 1
            hit_list.append(hit_record)
    return hit_list

def ids_missing_from_art_cat():
    '''
    Returns a list of art_ids that are not found in art_cat but are in one of the daily models
    '''
    count_basie_id = '3mATHi0690pFOIG0VhalBL'
    missing_in_both = daily_artists.ids_not_in_art_cat() + daily_tracks.ids_not_in_art_cat()
    if count_basie_id in missing_in_both:
        missing_in_both.remove(count_basie_id)
    return missing_in_both


class DailyCharts:
    '''
    One object, two different daily models as a parameter
    '''

    def __init__(
            self, 
            model,#daily_tracks 
            app,#result of push_app_context()
            spotify_username):
        #spotify
        self.spot_username = spotify_username
        self.sp = sp_obj(spotify_username)

        #flask-model
        self.model = model
        self.app = app

    def daily_green_light(self):
        latest_model_date = self.model.get_latest_date()
        today_date = date.today()

        if latest_model_date < today_date:
            return True

    def today_top_tracks(
        self,
        ):
        '''
        Accepts a string of one of the daily tables, requests the short-term top10 from Spotify, returns a JSON
        '''
        if self.model == daily_artists:
            today_top_results = self.sp.current_user_top_artists(time_range='short_term', limit=10)
        if self.model == daily_tracks:
            today_top_results = self.sp.current_user_top_tracks(time_range='short_term', limit=10)
        return today_top_results

    def today_top_chart_to_dicts(
        self,
    ):
        dicts = JSON_to_listofDicts(self.today_top_tracks(), self.model)
        return dicts
    
    def dict_to_model_obj(
            self,
            entry,
        ):
        if self.model == daily_tracks:
            new_entry = daily_tracks(
                    position=entry['position'],
                    art_id=entry['art_id'],
                    art_name=entry['art_name'],
                    album_name=entry['album_name'],
                    song_id=entry['song_id'],
                    song_name=entry['song_name'],
                    date=entry['date']
                )
        if self.model == daily_artists:
            new_entry = daily_artists(
                position=entry['position'],
                art_id=entry['art_id'],
                art_name=entry['art_name'],
                date=entry['date']
            )

        return new_entry

    def today_top_chart_obj(
        self,
    ):
        '''
        Returns a list of daily_chart or daily_tracks. 10 items. position 1-10. todays date.
        '''
        objs = list(map(
            self.dict_to_model_obj,
            self.today_top_chart_to_dicts()
        ))
        return objs
    

    def add_daily_to_db(self):
        '''
        takes the chart from today on Spotify, adds it to the model's database
        '''
        if self.daily_green_light():

            if self.today_top_chart_obj():
                for obj in self.today_top_chart_obj():
                    self.model.add_daily_chart_to_db(obj)
                print(f'Added to {self.model} model')
            else:
                print('No Dice.')
        else:
            print('Today chart data already saved.')