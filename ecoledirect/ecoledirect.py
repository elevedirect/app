import base64
import datetime
from ecoledirect.api import *
import json
import requests


class EcoleDirect:

    def __init__(self):
        self.endpoint = 'https://api.ecoledirecte.com/v3/'

    @staticmethod
    def format_payload(data):
        return {"data": json.dumps(data)}

    def _request(self, route: Route, data):
        payload = self.format_payload(data)
        url = self.endpoint + route.path + '?' + route.args
        headers = {
            'X-token': '',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0',
        }
        if 'token' in data.keys():
            headers['X-token'] = data['token']
        if 'id' in data.keys() and 'date' in data.keys():
            url = url % (str(data['id']), data['date'])
        elif 'id' in data.keys():
            url = url % str(data['id'])
        requests.options(url)
        response = requests.post(url, data=payload, headers=headers)
        try:
            if response.json()['code'] == 525:
                return {'expired': True}
        except:
            pass
        json_response = response.json()
        json_response['expired'] = False
        return json_response

    def get_work_date(self, token, identifiant, date):
        data = {
            "anneeScolaire": "",
            "token": token,
            "id": identifiant,
            "date": date
        }
        response = self._request(DATE_WORK, data)
        return response

    def get_notes(self, token, identifiant):
        try:
            data = {
                "anneeScolaire": "",
                "token": token,
                "id": identifiant
            }
            response = self._request(NOTES, data)
            if response['expired'] or response['code'] == 520:
                response['expired'] = True
                return response
            notes = response['data']['notes']
            periodes = response['data']['periodes']
            return {'notes': notes, 'periodes': periodes, 'expired': False}
        except Exception as error:
            print(f'Error while fetching notes: {error.__class__.__name__}')
            return None
            # raise error

    def get_work(self, token, identifiant):
        try:
            data = {
                "anneeScolaire": "",
                "token": token,
                "id": identifiant
            }
            response = self._request(WORK, data)
            if response['expired']:
                return response
            response_keys = response['data'].copy().keys()
            formatted_response = []
            for date in response_keys:
                new_response = self.get_work_date(token, identifiant, date)
                work = {'homeworks': response['data'][date], 'date': date}
                year, month, day = date.split('-')
                date_object = datetime.datetime(year=int(year), month=int(month), day=int(day))
                speaking_date = date_object.strftime("%A %d %B")
                work['showing_date'] = speaking_date
                for homework in work['homeworks']:
                    for detailed_homework in new_response['data']['matieres']:
                        if detailed_homework.get('aFaire'):
                            if detailed_homework['aFaire']['idDevoir'] == homework['idDevoir']:
                                homework['contenu'] = base64.b64decode(detailed_homework["aFaire"]["contenu"]).decode('utf-8')
                formatted_response.append(work)
            return formatted_response
        except Exception as error:
            print(f'Error while fetching work: {error.__class__.__name__}')
            return None
            # raise error

    def change_done(self, token, identifiant, id_devoir, effectue):
        effectue = not effectue
        if effectue:
            effectues_devoirs = [int(id_devoir)]
            non_effectues_devoirs = []
        else:
            effectues_devoirs = []
            non_effectues_devoirs = [int(id_devoir)]
        data = {
            "idDevoirsEffectues": effectues_devoirs,
            "idDevoirsNonEffectues": non_effectues_devoirs,
            "token": token,
            "id": identifiant
        }
        response = self._request(DONE_WORK, data)
        if response['expired']:
            return response

    def login(self, username, password):
        # try:
        data = {
            "identifiant": username,
            "motdepasse": password,
        }
        response = self._request(LOGIN, data)
        if response['expired']:
            return response
        print(response)
        token = response['token']
        prenom = response['data']['accounts'][0]['prenom']
        nom = response['data']['accounts'][0]['nom']
        photo = response['data']['accounts'][0]['profile']['photo']
        classe = response['data']['accounts'][0]['profile']['classe']['libelle']
        etablissement = response['data']['accounts'][0]['nomEtablissement']
        logo = 'https://api.ecoledirecte.com/v3/telechargement.awp?cToken=MDI1MTA2MlU=&verbe=get&fichierId=' + \
               response['data']['accounts'][0]['logoEtablissement'] + '&leTypeDeFichier=IMPORT_FTP'
        identifiant = response['data']['accounts'][0]['id']
        return {'token': token, 'nom': nom, 'prenom': prenom, 'photo': photo, 'classe': classe,
                'college': etablissement, 'logo': logo, 'id': identifiant}
        # except Exception as error:
        #     print(f'Error while login in: {error.__class__.__name__}')
        #     return None
            # raise error
