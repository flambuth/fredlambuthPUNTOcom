*/1 * * * * /home/flambuth/fredlambuthPUNTOcom/scripts/check_current_song.sh >> /home/flambuth/fredlambuthPUNTOcom/scripts/rp_output.log 2>&1

#daily_charts
15 6 * * * /home/flambuth/fredlambuthPUNTOcom/scripts/add_today_chart.sh  >> /home/flambuth/fredlambuthPUNTOcom/scripts/daily_errors.log 2>&1

#artcat_scan
20 6 * * * /home/flambuth/fredlambuthPUNTOcom/scripts/scan_for_new_art_ids.sh  >> /home/flambuth/fredlambuthPUNTOcom/scripts/artcat_errors.log 2>&1