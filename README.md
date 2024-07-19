<h2> I'm Fred Lambuth! </h2>
<p>This is the public Github repository where I keep the sourcecode for my website
<img align='right' src="https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExc2NxbmowZXFkdjFnbGVmYjgyZHl4azc2MGd1NGJybGFiZzRob2N6aiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ew57HYXAM8716OOtPm/giphy.gif" width="230">
</em></p>

[![Linkedin: Fred](https://img.shields.io/badge/-fredricklambuth-blue?style=flat-square&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/fredricklambuth/)](https://www.linkedin.com/in/fredricklambuth/)
[![GitHub Fred](https://img.shields.io/github/followers/flambuth?label=follow&style=social)](https://github.com/flambuth)




### <img src="https://media.giphy.com/media/VgCDAzcKvsR6OM0uWg/giphy.gif" width="50"> The project:

# fredlambuthPUNTOcom
This is around version 4.0 of fredlambuth.com. The first was a default Wordpress site. Version 2.0 began with Django, with nothing more than two pages, eventually showing my Spotify data. Version 3 was when I began using Flask as the framework to handle the web requests to my data. Putting everything into designated folders and cleaning up the top level project folder is where I'm at now. Let's say version 3.2.

### app
Flask files making all the routes for web users

### cron_jobs
Python files that hold functions that are performed regularly and referenced by a .sh file in /scripts

### global_spotify
ETL processes for creating the databases for a dashboard the flask app serves

### migrations
History of Changes to the data model of the flask app. 

### my_spotipy
Python files that hold functions that make requests to the Spotify API to retreive user listening data

### scripts
Bash files that are placed into crontab and the error logs for these cron tasks