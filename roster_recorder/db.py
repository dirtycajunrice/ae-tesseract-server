from roster_recorder import dontshareme, ATTACKER, DEFENDER
from pymongo import MongoClient
import datetime
import re
from bson.objectid import ObjectId

class Db():

    def __init__(self):
        self.client = MongoClient(dontshareme.CONNECTION_STRING)
        self.ae = self.client['ae']
        self.war_id = None
        self.attacker = {}
        self.defender = {}
        self.role = None
        self.company_id = None

    def UpdateWar(self, war_type=None, role=None, faction=None, company=None,
                  time=None, location=None, army=None, standby=None):

        if self.war_exists(war_type, time, location):
            return

        war_update = {}
        war_army = []

        war_update['warType'] = war_type

        company_id = self.get_company_id(company, faction)
        faction_id = self.get_faction_id(faction)
        self.company_id = company_id
        self.role = role
        if role == ATTACKER:
            self.attacker = {'companyId': company_id, 'name': company,
                             'faction': faction, 'factionId': faction_id, 'role': role}
            war_update['companies'] = [self.attacker]
        elif role == DEFENDER:
            self.defender = {'companyId': company_id, 'name': company,
                             'faction': faction, 'factionId': faction_id, 'role': role}
            war_update['companies'] = [self.defender]

        war_update['location'] = location
        war_update['time'] = time

        for player in army:
            player_id, name = self.get_player_id(player['name'])
            # if self.war_exists:
                # if self.ae.wars.find_one({'_id': self.war['_id'], 'army.playerId': player_id, 'group': 'STANDBY'}):
                #     # Remove player from standby list if they're in the army
                #     self.ae.wars.update_one({'_id': self.war['_id']},
                #                             {'$pull': {'army.playerId': player_id}}, upsert=False)
            war_army.append({
                'playerId': player_id,
                'name': name,
                'group': player['group']
            })

        for player in standby:
            player_id, name = self.get_player_id(player)
            # Only add standby player if they're not already in the roster
            war_id = None
            if self.war_exists:
                war_id = self.war_id
            if not self.ae.wars.find_one({'_id': war_id, 'army.playerId': player_id}):
                war_army.append({
                    'playerId': player_id,
                    'name': name,
                    'group': 'STANDBY'
                })
            # else:
            #     print(f'{player} already in')

        war_update['army'] = war_army

        # # Remove existing army to update with potential new values
        # self.ae.wars.update_many({'_id': self.war['_id']},
        #                          {'$pull': {'army': {'group': {'$ne': 'STANDBY'}}}},
        #                          upsert=False)
        #

        self.war_id = self.ae.wars.insert_one(war_update).inserted_id

    def UpdateStandby(self, standby):
        # Update with new full list of standby
        war_update = {}
        war_army = []
        for player in standby:
            player_id, name = self.get_player_id(player)
            # Only add standby player if they're not already in the roster
            # war_id = None
            # if self.war_exists:
            #     war_id = self.war['_id']
            if not self.ae.wars.find_one({'_id': self.war_id, 'army.playerId': player_id}):
                war_army.append({
                    'playerId': player_id,
                    'name': name,
                    'group': 'STANDBY'
                })

        war_update['army'] = {'$each': war_army}
        self.ae.wars.update_one({'_id': self.war_id}, {'$push': war_update})

    def war_exists(self, war_type: str, time: datetime.datetime, location: str) -> bool:
        self.war_id = self.ae.wars.find_one({'warType': war_type, 'time': time, 'location': location})
        if self.war_id is None:
            return False
        else:
            return True

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

    def get_company_id(self, name: str, faction: str):

        company_id = self.ae.companies.find_one({'name': name})
        if company_id is None:
            faction_id = self.get_faction_id(faction)
            self.ae.companies.insert_one({'name': name, 'faction': faction, 'factionId': faction_id})
            company_id = self.ae.companies.find_one({'name': name})

        return company_id['_id']

    def get_faction_id(self, name: str):
        faction_id = self.ae.factions.find_one({'name': name.upper()})
        return faction_id['_id']

    def UpdatePerformance(self, rankings, company_results):
        performance = []
        for player in rankings:
            player_id, _ = self.get_player_id(player[1])
            if not self.ae.wars.find_one({'_id': self.war_id, 'performance.playerId': player_id}):
                performance.append(
                    {'playerId': player_id, 'name': player[1], 'score': player[2], 'kills': player[3],
                     'deaths': player[4], 'assists': player[5], 'healing': player[6], 'damage': player[7]}
                )

        # self.ae.wars.update_one({'_id': self.war['_id']}, {'$push': self.war_update})

        if len(performance) > 0:
            self.ae.wars.update_one({'_id': self.war_id},
                                    {'$push': {'performance': {'$each': performance}}})

        for company in company_results:
            company_id = self.get_company_id(company['name'], company['faction'])
            # Update attacker/defender outcome if not already updated
            if not company_id == self.attacker.get('companyId') and self.attacker.get('outcome'):
                self.ae.wars.update_one({'_id': self.war_id, 'companies.companyId': company_id},
                                        {'$set': {'companies.$.outcome': company['outcome']}})
            elif not company_id == self.defender.get('companyId') and self.defender.get('outcome'):
                self.ae.wars.update_one({'_id': self.war_id, 'companies.companyId': company_id},
                                        {'$set': {'companies.$.outcome': company['outcome']}})
            # Else insert details if not already added
            elif not self.ae.wars.find_one({'_id': self.war_id, 'companies.companyId': company_id}):
                faction_id = self.get_faction_id(company['faction'])
                company_update = {'companyId': company_id,
                                  'name': company['name'],
                                  'factionId': faction_id,
                                  'faction': company['faction'],
                                  'outcome': company['outcome']}
                role = None
                if self.role == ATTACKER:
                    role = DEFENDER
                    self.attacker = company_update
                elif self.role == DEFENDER:
                    role = ATTACKER
                    self.defender = company_update

                company_update['role'] = role
                self.ae.wars.update_one({'_id': self.war_id}, {'$push': {'companies': company_update}})








