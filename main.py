from ecoledirect import EcoleDirect as ED
from flask import Flask, render_template, request, make_response, redirect, send_file
import json
import qrcode
import math
import markdown
import locale
from PIL import Image


locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")

app = Flask('Eleve Direct')
school = ED()


def generateQrcode(data, name):
    logo = Image.open(f'static/legal/elevedirectqr.png')
    basewidth = 50
    wpercent = (basewidth / float(logo.size[0]))
    hsize = int((float(logo.size[1]) * float(wpercent)))
    logo = logo.resize((basewidth, hsize))
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(data)
    qr.make()
    qrimg = qr.make_image(fill_color="black", back_color="white").convert('RGBA')
    pos = ((qrimg.size[0] - logo.size[0]) // 2, (qrimg.size[1] - logo.size[1]) // 2)
    qrimg.paste(logo, pos)
    qrimg.save(f'cache/{name}.png')


def round_up(n, decimals=0):
    if n:
        multiplier = 10 ** decimals
        return math.floor(n * multiplier + 0.5) / multiplier
    return n


def getPeriodes(periodes):
    return [(periode['codePeriode'], periode['ensembleMatieres']['disciplines'], periode['periode']) for periode in periodes if not periode['annuel']]


def parseNotes(notes):
    return [{'valeur': note['valeur'], 'sur': note['noteSur'], 'coef': note['coef'], 'periode': note['codePeriode'],
             'devoir': note['devoir'], 'matiere': note['libelleMatiere'], 'matiere_code': note['codeMatiere']} for note in notes]


def getDisciplines(matieres):
    disciplines = [{'nom': matiere['discipline'], 'has-sous-mat': False, 'is-sous-mat': False, 'coef': matiere['coef'], 'code': matiere['codeMatiere'], 'sous-matieres': [], 'notes': []} for matiere in matieres if not matiere['sousMatiere']]
    sous_matiere_disciplines = [{'nom': matiere['discipline'], 'has-sous-mat': False, 'is-sous-mat': True, 'coef': matiere['coef'], 'code': matiere['codeMatiere'], 'notes': []} for matiere in matieres if matiere['sousMatiere']]
    for sous_matiere in sous_matiere_disciplines:
        for matiere in disciplines:
            if matiere['code'] == sous_matiere['code']:
                matiere['has-sous-mat'] = True
                matiere['sous-matieres'].append(sous_matiere)
    return disciplines


def getNotes(notes, matieres, periode):
    for matiere in matieres:
        for note in notes:
            if note['periode'] == periode:
                if note['matiere_code'] == matiere['code'] and not matiere['has-sous-mat']:
                    matiere['notes'].append(note)
                elif note['matiere_code'] == matiere['code'] and matiere['has-sous-mat']:
                    for sous_matiere in matiere['sous-matieres']:
                        if note['matiere_code'] == sous_matiere['code'] and note['matiere'] == sous_matiere['nom']:
                            sous_matiere['notes'].append(note)
    return matieres


def calculateAverage(matieres):
    for matiere in matieres:
        if matiere['has-sous-mat']:
            matiere['sous-matieres'] = calculateAverage(matiere['sous-matieres'])
            count = 0
            sum_average = 0
            for sous_matiere in matiere['sous-matieres']:
                if sous_matiere['average']:
                    count += 1
                    sum_average += sous_matiere['average']
            if count != 0:
                matiere['average'] = round_up(sum_average / count, 2)
        else:
            sum_notes = 0
            coefficients_sum = 0
            for note in matiere['notes']:
                if note['valeur'] in ['Disp\xa0', 'Abs\xa0', 'NE\xa0', 'EA\xa0']:
                    continue
                if note['sur'] != '20':
                    note_sur = float(note['sur'].replace(',', '.'))
                    current_note = float(note['valeur'].replace(',', '.'))
                    new_note = current_note * 20 / note_sur
                    new_note = round_up(new_note, 2)
                    note['valeur'] = str(new_note)
                    note['sur'] = '20'
                note_value = float(note['valeur'].replace(',', '.'))
                coefficient = float(note['coef'].replace(',', '.'))
                sum_notes += note_value * coefficient
                coefficients_sum += coefficient
            if coefficients_sum != 0:
                matiere['average'] = round_up(sum_notes / coefficients_sum, 2)
            else:
                matiere['average'] = None
    return matieres


def load_dynamic(callback):
    cookie = request.cookies.get('account')
    account = json.loads(cookie)
    notes_data = school.get_notes(account['token'], account['id'])
    if notes_data['expired']:
        return redirect('/?expired=true')
    periodes = getPeriodes(notes_data['periodes'])
    notes = []
    for periode, disciplines, nom in periodes:
        matieres = getDisciplines(disciplines)
        populated_matieres = getNotes(parseNotes(notes_data['notes']), matieres, periode)
        periode_notes = calculateAverage(populated_matieres)
        all_average = [matiere['average'] for matiere in periode_notes if matiere['average']]
        final_average = sum(all_average) / len(all_average)
        final_average = round_up(final_average, 2)
        notes.append({'data': periode_notes, 'code': periode, 'nom': nom, 'average': final_average})
    work_data = school.get_work(account['token'], account['id'])
    # day_work_data = school.get_work_date(account['token'], account['id'], '2022-06-10')
    return render_template(callback, account=account, notes=notes, work=work_data)


@app.route('/')
def root():
    expired = request.args.get('expired')
    error = request.args.get('error')
    return render_template('login.html', expired=expired, error=error)


@app.route('/home')
def home():
    return load_dynamic('home.html')


@app.route('/cgu')
def cgu():
    return markdown.markdown(open('static/legal/CGU.md').read())


@app.route('/cantine-qr')
def qr():
    cookie = request.cookies.get('account')
    account = json.loads(cookie)
    student_id = str(account['id'])
    zero_times = 3 - len(student_id)
    last_number = '1' + ('0' * zero_times) + student_id + "0"
    data = f"eleve||{student_id}||{last_number}"
    generateQrcode(data, student_id)
    return send_file(f'cache/{student_id}.png')


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    credentials = school.login(username, password)
    if credentials:
        response = make_response(redirect('/home'))
        response.set_cookie('account', json.dumps(credentials))
        return response
    return render_template('login.html', failed='true')


@app.errorhandler(Exception)
def error(_error):
    print(_error)
    return redirect('/?error=true')


if __name__ == '__main__':
    app.run(port=9090, host='0.0.0.0', debug=True)
