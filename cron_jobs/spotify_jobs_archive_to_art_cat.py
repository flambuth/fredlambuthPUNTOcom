from scripts import backend_methods, rp_archives

from app.utils import push_app_context
from app.models.catalogs import artist_catalog


def scan_rp_archives_for_MIAs(
    db_path,
    archive_csv_path,
    app=push_app_context()
):
    ac_backdoor_tool = backend_methods.ArtCat_Backend(db_path)
    archive_tool = rp_archives.RP_Archive_CSV(archive_csv_path)
    
    currentlyMIA = ac_backdoor_tool.mias_ready_for_catalog(archive_tool, 35)
    
    if currentlyMIA:
        for ac_entry in currentlyMIA:
            artist_catalog.add_new_art_cat_to_db(ac_entry)
            print(f"{ac_entry} has been added to the artist Catalog model!")
            
if __name__ == '__main__':
    test_db_path = '/home/flambuth/fredlambuthPUNTOcom/data/fred.db'
    test_archive_csv_path = '/home/flambuth/archives/recently_played.csv'
    scan_rp_archives_for_MIAs(
        test_db_path,
        test_archive_csv_path
    )