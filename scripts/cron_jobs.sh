#rp feed
*/1 * * * * /home/flambuth/fredlambuthPUNTOcom/scripts/check_current_song.sh >> /home/flambuth/fredlambuthPUNTOcom/scripts/rp_output.log 2>&1

#daily_charts
15 6 * * * /home/flambuth/fredlambuthPUNTOcom/scripts/add_today_chart.sh  >> /home/flambuth/fredlambuthPUNTOcom/scripts/daily_errors.log 2>&1

#artcat_scan
20 6 * * * /home/flambuth/fredlambuthPUNTOcom/scripts/scan_for_new_ids.sh  >> /home/flambuth/fredlambuthPUNTOcom/scripts/artcat_errors.log 2>&1

#global_csv_refresh
50 13 * * *  ~/fredlambuthPUNTOcom/scripts/refresh_global_csv.sh >> /home/flambuth/archives/global_cron_errors.log 2>&1
#global_db_refresh, takes about 100 seconds
55 13 * * *  cd /home/flambuth/fredlambuthPUNTOcom && /usr/bin/python3 /home/flambuth/fredlambuthPUNTOcom/global_spotify/transform.py >> /home/flambuth/fredlambuthPUNTOcom/scripts/global_etl_cron_errors.log 2>&1

#shuffle RPs to archive
0 0 1,11,21 * * cd /home/flambuth/fredlambuthPUNTOcom && /usr/bin/python3 /home/flambuth/fredlambuthPUNTOcom/scripts/backend_rps.py >> /home/flambuth/fredlambuthPUNTOcom/scripts/rp_shuffle_errors.log 2>&1