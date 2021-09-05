from roster_recorder.decoder import Decoder
from roster_recorder.webserver import Webserver


if __name__ == "__main__":
    webserver = Webserver()
    webserver.Run()

    decoder = Decoder()
    x_range, y_range = decoder.Decode('images\\roster_example2.png')
    # extract roster
    roster = []
    group = 0
    player = 0
    for x in x_range:
        for y in y_range:
            try:
                roster[group].append(decoder.GetName(x, y))
            except IndexError:
                roster.append([decoder.GetName(x, y)])
            # print(f"Adding Player {player} to group {group}")
            if player == 4:
                player = 0
                group += 1
                continue

            player += 1

    i = 1
    for group in roster:
        print(f'Group {i}: {", ".join(group)}')
        i += 1
