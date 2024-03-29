import base64
import datetime
import urllib.request
import urllib
from ecoledirect.api import *
import json
import requests
import locale


locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")


def convert_dict_to_bytes(dict_):
    new_dict = {}
    for key in dict_.keys():
        if type(dict_[key]) != int:
            new_dict[key.encode()] = str(dict_[key]).encode()
        else:
            new_dict[key.encode()] = dict_[key]
    return new_dict


def get_french_date(date):
    year, month, day = date.split('-')
    date_object = datetime.datetime(year=int(year), month=int(month), day=int(day))
    french_date = date_object.strftime("%A %d %B")
    return french_date


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
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0',
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
        if response['expired'] or response['code'] == 520:
            response['expired'] = True
            return response
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

    def get_timeline(self, token, identifiant):
        try:
            data = {
                "token": token,
                "id": identifiant
            }
            response = self._request(TIMELINE, data)
            if response['expired'] or response['code'] == 520:
                response['expired'] = True
                return response
            data = response['data']
            elements = []
            for el in data:
                el_type = el['typeElement']
                if el_type == 'Messagerie':
                    icon = 'fas fa-envelope'
                elif el_type == 'Note':
                    icon = 'fas fa-award'
                elif el_type == 'Document':
                    icon = 'fas fa-folder-open'
                else:
                    icon = 'fas fa-calendar-plus'
                el['icon'] = icon
                el['french_date'] = get_french_date(el['date'])
                elements.append(el)
            return elements
        except Exception as error:
            print(f'Error while fetching timeline: {error.__class__.__name__}')
            return None
            # raise error

    def get_document(self, document, token, do_not_translate_name=False, download=True):
        doc_id = document['id']
        doc_type = document['type']
        if not do_not_translate_name:
            doc_name = document['libelle'].encode('latin-1').decode('utf-8')
        else:
            doc_name = document['libelle']
        encoded_id = urllib.parse.quote(str(doc_id).encode())
        encoded_type = urllib.parse.quote(doc_type.encode())
        encoded_name = urllib.parse.quote(doc_name.encode())
        url = f"/file/{encoded_id}/{encoded_type}/{encoded_name}"
        if download:
            data = {
                "forceDownload": 0,
                "token": token
            }
            if not do_not_translate_name:
                doc_name = document['libelle'].encode('latin-1').decode('utf-8')
            else:
                doc_name = document['libelle']
            new_doc_route = DOCUMENTS
            args = new_doc_route.args
            args = args % (doc_id, doc_type)
            doc_content = self._request(DOCUMENTS, data, args, True)
            return {"content": doc_content, "name": doc_name, "url": url, "id": doc_id}
        return {"name": doc_name, "url": url, "id": doc_id}

    def get_work(self, token, identifiant, days_list, include_tests=False):
        try:
            formatted_response = []
            tests = []
            for day in days_list:
                day_work = self.get_work_date(token, identifiant, day)
                if day_work['expired']:
                    return True, []
                work = {'homeworks': day_work['data']['matieres'], 'date': day}
                year, month, day = day.split('-')
                date_object = datetime.datetime(year=int(year), month=int(month), day=int(day))
                speaking_date = date_object.strftime("%A %d %B")
                work['showing_date'] = speaking_date
                for homework in work['homeworks']:
                    homework['seance'] = {}
                    homework['date'] = day
                    homework['french_date'] = speaking_date
                    if 'aFaire' in homework.keys():
                        homework['has_homework'] = True
                        if homework['aFaire']['idDevoir'] == homework['id']:
                            homework['contenu'] = base64.b64decode(homework["aFaire"]["contenu"]).decode('utf-8')
                            if len(homework['aFaire']['documents']) > 0:
                                homework['has_documents'] = True
                                documents = []
                                for doc in homework['aFaire']['documents']:
                                    documents.append(self.get_document(doc, token, download=False))
                                homework['documents'] = documents
                            if len(homework['aFaire']['documents']) == 0:
                                homework['documents'] = []
                                homework['has_documents'] = False
                            homework['effectue'] = homework['aFaire']['effectue']
                            if homework['interrogation']:
                                tests.append(homework)
                    else:
                        homework['contenu'] = 'Rien à afficher'
                        homework['has_homework'] = False
                    if 'contenuDeSeance' in homework.keys():
                        homework['has_seance'] = True
                        if homework['contenuDeSeance']['idDevoir'] == homework['id']:
                            homework['seance']['contenu'] = base64.b64decode(homework["contenuDeSeance"]["contenu"]).decode('utf-8')
                            if len(homework['contenuDeSeance']['documents']) > 0:
                                homework['seance']['has_documents'] = True
                                documents = []
                                for doc in homework['contenuDeSeance']['documents']:
                                    documents.append(self.get_document(doc, token, download=False))
                                homework['seance']['documents'] = documents
                            if len(homework['contenuDeSeance']['documents']) == 0:
                                homework['seance']['documents'] = []
                                homework['seance']['has_documents'] = False
                    else:
                        homework['seance']['contenu'] = 'Rien à afficher'
                        homework['has_seance'] = False
                formatted_response.append(work)
            if include_tests:
                return formatted_response, tests
            return formatted_response
        except Exception as error:
            print(f'Error while fetching work: {error.__class__.__name__}')
            # return None, None
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
