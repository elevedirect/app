import base64
import datetime
import urllib

from ecoledirect.api import *
import json
import requests


class EcoleDirect:

    def __init__(self):
        self.endpoint = 'https://api.ecoledirecte.com/v3/'

    @staticmethod
    def format_payload(data):
        return {"data": json.dumps(data)}

    def _request(self, route: Route, data, special_args=None, plain=False):
        if special_args:
            args = special_args
        else:
            args = route.args
        payload = self.format_payload(data)
        url = self.endpoint + route.path + '?' + args
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
        if not plain:
            json_response = response.json()
            json_response['expired'] = False
            return json_response
        return response.content

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

    def get_document(self, document, token, do_not_translate_name=False):
        data = {
            "forceDownload": 0,
            "token": token
        }
        doc_id = document['id']
        doc_type = document['type']
        if not do_not_translate_name:
            doc_name = document['libelle'].encode('latin-1').decode('utf-8')
        else:
            doc_name = document['libelle']
        new_doc_route = DOCUMENTS
        args = new_doc_route.args
        args = args % (doc_id, doc_type)
        doc_content = self._request(DOCUMENTS, data, args, True)
        encoded_id = urllib.parse.quote(str(doc_id).encode())
        encoded_type = urllib.parse.quote(doc_type.encode())
        encoded_name = urllib.parse.quote(doc_name.encode())
        url = f"/file/{encoded_id}/{encoded_type}/{encoded_name}"
        return {"content": doc_content, "name": doc_name, "url": url, "id": doc_id}

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
                            if len(detailed_homework['aFaire']['documents']) > 0:
                                homework['has_documents'] = True
                                documents = []
                                for doc in detailed_homework['aFaire']['documents']:
                                    documents.append(self.get_document(doc, token))
                                homework['documents'] = documents
                            if len(detailed_homework['aFaire']['documents']) == 0:
                                homework['documents'] = []
                                homework['has_documents'] = False
                formatted_response.append(work)
            return formatted_response
        except Exception as error:
            # print(f'Error while fetching work: {error.__class__.__name__}')
            # return None
            raise error

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

    @staticmethod
    def hour_is_before_reference(hour, reference):
        hour_hour, hour_minute = hour.split(':')
        reference_hour, reference_minute = reference.split(':')
        if int(hour_hour) < int(reference_hour):
            return True
        elif int(hour_hour) == int(reference_hour) and int(hour_minute) < int(reference_minute):
            return True
        return False

    def order_classes(self, classes, next_hour, next_hour_minute, index=0, new_classes={}):
        current_index = index
        closer = {"start": f"0000-00-00 23:59", "end": f"0000-00-00 23:59"}
        if current_index > len(classes):
            return new_classes
        for classe in classes:
            classe_hour, classe_hour_minute = classe['start'].split(' ')[-1].split(':')
            if int(classe_hour) > int(next_hour):
                if self.hour_is_before_reference(f"{classe_hour}:{classe_hour_minute}", closer['start'].split(' ')[-1]):
                    closer = classe
            elif int(classe_hour) == int(next_hour) and int(classe_hour_minute) > int(next_hour_minute):
                if self.hour_is_before_reference(f"{classe_hour}:{classe_hour_minute}", closer['start'].split(' ')[-1]):
                    closer = classe
        new_classes[str(current_index)] = closer
        next_hour, next_hour_minute = closer['end'].split(' ')[-1].split(':')
        return self.order_classes(classes, next_hour, next_hour_minute, current_index + 1, new_classes)

    def get_timing(self, token, identifiant, start, end):
        data = {
            "dateDebut": start,
            "dateFin": end,
            "avecTrous": False,
            "token": token,
            "id": identifiant
        }

        response = self._request(TIMING, data)
        timing = {'empty': False, 'classes': []}
        if len(response['data']) == 0:
            timing['empty'] = True
        formatted_classe = {}
        for classe in response['data']:
            formatted_classe['name'] = classe['text']
            formatted_classe['matiere'] = classe['matiere']
            formatted_classe['salle'] = classe['salle']
            formatted_classe['prof'] = classe['prof']
            formatted_classe['color'] = classe['color']
            formatted_classe['contenuseance'] = classe['contenuDeSeance']
            formatted_classe['devoirs'] = classe['devoirAFaire']
            formatted_classe['start'] = classe['start_date']
            formatted_classe['end'] = classe['end_date']
            timing['classes'].append(formatted_classe)
            formatted_classe = {}
        next_hour, next_hour_minute = '23:59'.split(':')
        first_class = {}
        for classe in timing['classes']:
            classe_hour, classe_hour_minute = classe['start'].split(' ')[-1].split(':')
            if int(classe_hour) < int(next_hour):
                next_hour, next_hour_minute = classe_hour, classe_hour_minute
                first_class = classe
            elif int(classe_hour) == int(next_hour) and int(classe_hour_minute) < int(next_hour_minute):
                next_hour, next_hour_minute = classe_hour, classe_hour_minute
                first_class = classe
        timing['classes'] = self.order_classes(timing['classes'], next_hour, next_hour_minute, 1)
        timing['classes']['0'] = first_class
        return timing

    def login(self, username, password):
        try:
            data = {
                "identifiant": username,
                "motdepasse": password,
            }
            response = self._request(LOGIN, data)
            if response['expired']:
                return response
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
        except Exception as error:
            print(f'Error while login in: {error.__class__.__name__}')
            return None
            # raise error
