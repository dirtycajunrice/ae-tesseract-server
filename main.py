from roster_recorder.rosterdecoder import RosterDecoder
from roster_recorder.rankingsdecoder import RankingsDecoder
from roster_recorder.imgtypedetector import ImgTypeDetector
from roster_recorder.db import Db
from roster_recorder.webserver import Webserver
from roster_recorder import helpers, ROSTER, RANKINGS, STANDBY

if __name__ == "__main__":
    # webserver = Webserver()
    # webserver.Run()

    # Rankings images
    # img_path = 'images\\rankings_example_1.png'
    # img_path = 'images\\rankings_example_2.png'
    # img_path = 'images\\rankings_example_playerleft_1.png'
    # img_path = 'images\\rankings_example_playerleft_2.png'

    # War/Invasion images
    # img_path = 'images\\war_roster_example.png'
    # img_path = 'images\\war_roster_example_bw1.jpg'
    # img_path = 'images\\war_roster_example_bw2.jpg'
    # img_path = 'images\\war_roster_example_bw3.jpg'
    # img_path = 'images\\war_roster_example_bw4.jpg'
    #  img_path = 'images\\invasion_roster_example.png'


    images = [
                {'img_path': 'images\\war_roster_example_bw1.jpg', 'type': ROSTER},
                {'img_path': 'images\\war_roster_example_bw2.jpg', 'type': STANDBY},
                {'img_path': 'images\\rankings_example_bw1.png', 'type': RANKINGS},
                {'img_path': 'images\\rankings_example_bw2.png', 'type': RANKINGS}
             ]

    db = Db()
    for img in images:

        # typeDetector = ImgTypeDetector()
        # img_type = typeDetector.Detect(img_path)

        if img['type'] == ROSTER:
            decoder = RosterDecoder()
            war_type, role, faction, guild, time, location, army, standby, page = decoder.Decode(img['img_path'],
                                                                                                 img['type'])

            # helpers.print_war(war_type, role, faction, guild, time, location, army, standby, page)

            # Update database
            db.UpdateWar(war_type, role, faction, guild, time, location, army, standby)

        elif img['type'] == STANDBY:
            decoder = RosterDecoder()
            standby = decoder.Decode(img['img_path'], img['type'])
            db.UpdateStandby(standby)

        elif img['type'] == RANKINGS:
            decoder = RankingsDecoder()
            rankings, company_results = decoder.Decode(img['img_path'])

            # helpers.print_rankings(rankings, date)

            # Update database
            db.UpdatePerformance(rankings, company_results)

