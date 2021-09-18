import cv2

def drawDebugRectangle(image: str, xy, wh):
    cv2.rectangle(image, xy, (xy[0] + wh[0], xy[1] + wh[1]), (0, 0, 255), 2)

def showImage(image: str):
    cv2.imshow('output', image)
    cv2.waitKey(0)

#class Anchor:
#    def __init__(self):
#        self.width =


def roster_json(wartype, time, location, army, standby, page):
    import json

    data = {}
    data['roster'] = []

    army_list = []
    i = 1
    for group in army:
        for player in group:
            army_list.append({
                'Name': player,
                'Group': str(i)
            })

        i += 1
    standby_list = []
    i = 1
    for player in standby:
        standby_list.append({
            'Name': player
        })

        i += 1

    data['roster'].append({
        'WarType': wartype,
        'Date': str(time[0]),
        'Location': location[0],
        'CurrentPage': page[0],
        'TotalPages': page[1],
        'Army': army_list,
        'Standby': standby_list
    })
    print(data)

    with open('data.txt', 'w') as outfile:
        json.dump(data, outfile)

    return data

def print_war(war_type, role, faction, guild, time, location, army, standby, page):
    print(f'Type: {war_type}')
    print(f'Role: {role}')
    print(f'Guild: {guild}')
    print(f'Faction: {faction}')
    print(f'Date: {time}')
    print(f'Location: {location}')

    for player in army:
        print(f'{player}')

    # print(f'Page {page[0]} of {page[1]}')
    print(f'Standby: {", ".join(standby)}')

def print_rankings(rankings, date):
    print(f'Parse Date: {date}')
    for player in rankings:
        print(
            f'Rank: {player[0]}, Name: {player[1]}, Score: {player[2]}, Kills: {player[3]}, Deaths: {player[4]}, '
            f'Assists: {player[5]}, Healing: {player[6]}, Damage: {player[7]}')