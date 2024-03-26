from datetime import timedelta
from PIL import Image
import os
from app import create_app

def push_app_context():
    '''
    Call this so you can interact with flask models outside of deploying the 
    flask app
    '''
    my_flask_app = create_app()
    app_ctx = my_flask_app.app_context()
    app_ctx.push()
    return my_flask_app
    

def find_streaks_in_dates(dates):
    '''
    Given a list of dates, returns a dictionary with the start date
    of each streak as the key, the length of streak in days as an integer 
    value.
    '''
    # Check if dates is None
    if dates is None:
        raise ValueError("Input dates cannot be None.")

    # Check if dates is an empty list
    if not dates:
        return {}  # Return an empty dictionary if there are no dates


    streaks = {}
    current_streak_start = None
    current_streak_length = 0

    for date in sorted(dates):
        if current_streak_start is None:
            current_streak_start = date
            current_streak_length = 1
        elif date == current_streak_start + timedelta(days=current_streak_length):
            current_streak_length += 1
        else:
            streaks[current_streak_start.isoformat()] = current_streak_length
            current_streak_start = date
            current_streak_length = 1

        # Add the last streak to the dictionary if there is one
        if current_streak_start is not None:
            streaks[current_streak_start.isoformat()] = current_streak_length

    streaks =   {
        k: v for k,v in streaks.items() if v>=2
    }
    return streaks

def evaluate_longest_streak(streaks1, streaks2):
    '''
    Accepts two dicionaries. Returns the largest value between both dictionaries
    Ostensibly this is for comparing two 'streaks' dicts that output from 
    the 'find_streaks_in_dates' function.
    '''
    all_streaks = {**streaks1, **streaks2}
    longest_streak = max(all_streaks.items(), key=lambda x: x[1])
    return longest_streak



def resize_imageOLD(input_path, output_path, size=(100, 100)):
    """
    Resize an image to a specified size.

    Parameters:
    - input_path (str): Path to the input image file.
    - output_path (str): Path to save the resized image.
    - size (tuple): Desired size in pixels (width, height). Default is (100, 100).
    """
    #output_path = input_path.split('.')[0] + '.jpg'
    with Image.open(input_path) as img:
        img = img.resize(size)
        #img.convert('RGB').save(output_path, 'JPEG', quality=95)
        img.save(output_path)

def resize_image(input_path, size=(100, 100)):
    """
    Resize an image to a specified size and save it as JPEG format.

    Parameters:
    - input_path (str): Path to the input image file.
    - output_path (str): Path to save the resized image as JPEG.
    - size (tuple): Desired size in pixels (width, height). Default is (100, 100).
    """
    output_path = input_path.split('.')[0] + '.jpg'
    with Image.open(input_path) as img:
            img = img.resize(size)
            #img.convert('RGB').save(output_path, 'JPEG', quality=95)
            if input_path.lower().endswith(('.png', '.jpeg')):
                os.remove(input_path)
            return img

    if input_path.lower().endswith(('.png', '.jpeg')):
        os.remove(input_path)
