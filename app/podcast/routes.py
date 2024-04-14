from app.podcast import bp
from flask import send_file, render_template
import os
from flask_login import login_required

def extract_ep_id(episode_file):
    underscore_index = episode_file.index('_')
    dot_index = episode_file.index('.')

    # Extract the substring between '_' and '.'
    number_str = episode_file[underscore_index + 1:dot_index]

    # Convert the substring to an integer
    episode_id = int(number_str)
    return episode_id

@bp.route('/podcast', methods=['GET'])
@bp.route('/podcast/', methods=['GET'])
@login_required
def podcast_landing_page():
    audio_dir = '/home/flambuth/fredlambuthPUNTOcom/app/static/audio'
    file_list = os.listdir(audio_dir)
    episode_index = list(map(
        extract_ep_id,
        file_list
    ))

    return render_template('podcast/podcast_landing_page.html', files=episode_index)

@bp.route('/podcast/<int:podcast_id>')
@login_required
def serve_podcast_file(podcast_id):
    filename = f'static/audio/podcast_{podcast_id}.mp3'
    return send_file(filename, as_attachment=False)