from roster_recorder.decoder import Decoder
from roster_recorder.webserver import Webserver


if __name__ == "__main__":
    # webserver = Webserver()
    # webserver.Run()

    decoder = Decoder()
    # wartype, time, location, army, standby, page = decoder.Decode('images\\invasion_roster_example.png')
    wartype, time, location, army, standby, page = decoder.Decode('images\\war_roster_example.png')

    print(f'Type: {wartype}')
    print(f'Date: {time[0]}')
    print(f'Location: {location[0]}')

    i = 0
    for group in army:
        print(f'Group {i}: {", ".join(group)}')
        i += 1

    print(f'Page {page[0]} of {page[1]}')
    print(f'Standby: {", ".join(standby)}')