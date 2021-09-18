from roster_recorder.rosterdecoder import RosterDecoder
from roster_recorder.rankingsdecoder import RankingsDecoder
from roster_recorder.imgtypedetector import ImgTypeDetector
from roster_recorder.db import Db
from roster_recorder.webserver import Webserver
from roster_recorder import helpers, ROSTER, RANKINGS

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

    def poo(img_path):
        typeDetector = ImgTypeDetector()
        img_type = typeDetector.Detect(img_path)

        if img_type == RANKINGS:
            decoder = RankingsDecoder()
            rankings, date = decoder.Decode(img_path)

            helpers.print_rankings(rankings, date)

        elif img_type == ROSTER:
            decoder = RosterDecoder()
            war_type, role, faction, guild, time, location, army, standby, page = decoder.Decode(img_path)

            # helpers.print_war(war_type, role, faction, guild, time, location, army, standby, page)

            # Update database
            db = Db()
            if db.WarExists(war_type, time, location):
                db.UpdateWar(army=army, standby=standby)
            else:
                db.UpdateWar(war_type, role, faction, guild, time, location, army, standby)

        else:
            # TODO: Image not recognized
            pass


    images = ['images\\invasion_roster_example.png',
              'images\\war_roster_example.png',
              'images\\war_roster_example_bw1.jpg', 'images\\war_roster_example_bw2.jpg',
              'images\\war_roster_example_bw3.jpg', 'images\\war_roster_example_bw4.jpg',
              'images\\invasion_roster_example.png'
              ]
    for img in images:
        poo(img)






