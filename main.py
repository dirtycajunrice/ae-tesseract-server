from roster_recorder.rosterdecoder import RosterDecoder
from roster_recorder.rankingsdecoder import RankingsDecoder
from roster_recorder.webserver import Webserver
import json
from roster_recorder import helpers

if __name__ == "__main__":
    # webserver = Webserver()
    # webserver.Run()
    #
    # #TODO determine image type: roster or rankings
    #
    # decoder = RankingsDecoder()
    # rankings, date = decoder.Decode('images\\rankings_example_1.png')
    # print(f'War Date: {date}')
    # for player in rankings:
    #     print(f'Rank: {player[0]}, Name: {player[1]}, Score: {player[2]}, Kills: {player[3]}, Deaths: {player[4]}, Assists: {player[5]}, Healing: {player[6]}, Damage: {player[7]}')
    #


    decoder = RosterDecoder()
    # wartype, time, location, army, standby, page = decoder.Decode('images\\invasion_roster_example.png')
    wartype, time, location, army, standby, page = decoder.Decode('images\\war_roster_example.png')

    helpers.roster_json(wartype, time, location, army, standby, page)

    # print(f'Type: {wartype}')
    # print(f'Date: {time[0]}')
    # print(f'Location: {location[0]}')
    #
    # i = 0
    # for group in army:
    #     print(f'Group {i}: {", ".join(group)}')
    #     i += 1
    #
    # print(f'Page {page[0]} of {page[1]}')
    # print(f'Standby: {", ".join(standby)}')

