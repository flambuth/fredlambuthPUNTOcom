ATTACH DATABASE 'fredlambuth.db' AS old_db;
ATTACH DATABASE 'fred.db' AS new_db;

-- Transfer data from artist_catalog
INSERT INTO new_db.artist_catalog SELECT * FROM old_db.artist_catalog;

-- Transfer data from blog_users to user_accounts
INSERT INTO new_db.user_accounts SELECT * FROM old_db.blog_users;

-- Transfer data from playlists
INSERT INTO new_db.playlists SELECT * FROM old_db.playlists;

-- Transfer data from blog_comments
INSERT INTO new_db.blog_comments SELECT * FROM old_db.blog_comments;

-- Transfer data from daily_artists
INSERT INTO new_db.daily_artists SELECT * FROM old_db.daily_artists;

-- Transfer data from recently_played
INSERT INTO new_db.recently_played SELECT * FROM old_db.recently_played;

-- Transfer data from blog_posts
INSERT INTO new_db.blog_posts SELECT * FROM old_db.blog_posts;

-- Transfer data from daily_tracks
INSERT INTO new_db.daily_tracks SELECT * FROM old_db.daily_tracks;

-- Transfer data from track_catalog
INSERT INTO new_db.track_catalog SELECT * FROM old_db.track_catalog;

-- Detach old and new databases
DETACH DATABASE old_db;
DETACH DATABASE new_db;