from roster_recorder import dontshareme, ATTACKER, DEFENDER
from pymongo import MongoClient
import datetime
import re

class Db():

    def __init__(self):
        self.client = MongoClient(dontshareme.CONNECTION_STRING)
        self.ae = self.client['ae']
        self.war = None
        self.war_update = {}
        self.war_army = None
        self.war_exists = None

    def UpdateWar(self, war_type=None, role=None, faction=None, guild=None, time=None, location=None, army=None, standby=None):

        if war_type is not None:
            self.war_update['warType'] = war_type

        if role is not None and guild is not None:
            # guild_id = self.get_guild_id(guild, faction)
            if role == ATTACKER:
                self.war_update['attacker'] = {'guild': guild, 'faction': faction}
            elif role == DEFENDER:
                self.war_update['defender'] = {'guild': guild, 'faction': faction}

        if location is not None:
            self.war_update['location'] = location

        if time is not None:
             self.war_update['time'] = time

        if army is not None:
            if self.war_army is None:
                self.war_army = []

            for player in army:
                player_id, name = self.get_player_id(player['name'])
                if self.war_exists:
                    if self.ae.wars.find_one({'_id': self.war['_id'], 'army.playerId': player_id, 'group': 'STANDBY'}):
                        # Remove player from standby list if they're in the army
                        self.ae.wars.update_one({'_id': self.war['_id']},
                                                {'$pull': {'army.playerId': player_id}}, upsert=False)
                self.war_army.append({
                    'playerId': player_id,
                    'name': name,
                    'group': player['group']
                })

            self.war_update['army'] = self.war_army

        if standby is not None:
            if self.war_army is None:
                self.war_army = []

            for player in standby:
                player_id, name = self.get_player_id(player)
                # Only add standby player if they're not already in the roster
                war_id = None
                if self.war_exists:
                    war_id = self.war['_id']
                if self.ae.wars.find_one({'_id': war_id, 'army.playerId': player_id}) is None:
                    self.war_army.append({
                        'playerId': player_id,
                        'name': name,
                        'group': 'STANDBY'
                    })
                # else:
                #     print(f'{player} already in')


            self.war_update['army'] = self.war_army

        if self.war_exists:
            # Remove existing army to update with potential new values
            self.ae.wars.update_many({'_id': self.war['_id']},
                                     {'$pull': {'army': {'group': {'$ne': 'STANDBY'}}}},
                                     upsert=False)

            # Update with new full list of army and standby
            self.war_update['army'] = {'$each': self.war_army}
            self.ae.wars.update_one({'_id': self.war['_id']}, {'$push': self.war_update})

        else:
            self.ae.wars.insert_one(self.war_update)

    def WarExists(self, war_type: str, time: datetime.datetime, location: str) -> bool:
        self.war = self.ae.wars.find_one({'warType': war_type, 'time': time, 'location': location})
        if self.war is None:
            self.war_exists = False
            return self.war_exists
        else:
            self.war_exists = True
            return self.war_exists

    # def get_guild_id(self, name: str, faction: str):
    #     guild = self.ae.guilds.find_one({'name': name})
    #     if guild is None:
    #         self.ae.guilds.insert_one({'name': name, 'faction': faction})
    #         guild = self.ae.guilds.find_one({'name': name})
    #     elif faction is not None and guild['faction'] != faction:
    #         self.ae.guilds.update_one({'_id': guild['_id']}, {'$push': {'faction': faction}})
    #
    #     return guild['_id']

    def get_player_id(self, name: str):
        # Names longer than 15 can get cutoff due to the crown on the roster
        # Usually shouldn't be duplicate issues here, make a workaround if it does cause a problem
        length = len(name)
        if length > 15:
            name = name[0:15]

        player_id = self.ae.players.find_one({'name': {'$regex': '^{}.*'.format(name)}})
        if player_id is None:
            self.ae.players.insert_one({'name': name})
            player_id = self.ae.players.find_one({'name': name})

        return player_id['_id'], name

