const sections = document.querySelectorAll('.main')
const actions = document.querySelectorAll('.data-action')
const homeworksContainer = document.getElementById('homeworks-container')
const nextWorkButton = document.getElementById('nextwork')
const previousWorkButton = document.getElementById('previouswork')
let dataAction, dates, from, to, fromDateObject, fromYear, fromMonth, fromDay, fromDateString, toDateObject, toYear,
    toMonth, toDay, toDateString, currentDateObject, currentDateString, sampleDate, previousWeek, nextWeek, sampleDateString, sampleData
var frenchDate

Date.prototype.addDays = function (days) {
    let date = new Date(this.valueOf());
    date.setDate(date.getDate() + days);
    return date;
}

Date.prototype.removeDays = function (days) {
    let date = new Date(this.valueOf());
    date.setDate(date.getDate() - days);
    return date;
}

Date.prototype.getFullMonth = function () {
    let date = new Date(this.valueOf());
    let month = date.getMonth().toString()
    return ("0" + month).slice(-2);
}

Date.prototype.getFullDay = function () {
    let date = new Date(this.valueOf());
    let day = date.getDate().toString()
    return ("0" + day).slice(-2);
}

actions.forEach(action => {
    action.addEventListener('click', () => {
        dataAction = action.getAttribute('data-action')
        sections.forEach(section => {
            section.style = 'display: none;'
            if (section.className === `main ${dataAction}`) {
                section.style = ''
            }
        })
    })
})

function notePopup(element) {
    element.querySelector('.modal').classList.toggle('is-active')
}

function workPopup(elementId) {
    document.getElementById(elementId).classList.toggle('is-active')
}

function expand(periode) {
    document.getElementById(periode).classList.toggle('active')
    document.getElementById(periode + 'icon').classList.toggle('active')
}

async function share() {
    await navigator.share({
        'url': 'http://eleve-direct.server.camarm.fr',
        'text': 'Moyennes, carte de cantine et plus encore avec Eleve Direct !',
        'title': 'Rejoins Eleve Direct !'
    })
}

function toggleNavbar() {
    document.querySelector('.nav-wrapper').classList.toggle('active')
    document.querySelector('#burger').classList.toggle('is-active')
}

function logout() {
    document.cookie.split(";").forEach(function(c) { document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); });
    location.href = '/'
}

window.onload = () => {
    let anchor = location.hash.replaceAll('#', '')
    if (anchor === undefined || anchor === null || anchor === '') {
        console.log('Loading homepage')
        sections.forEach(section => {
            section.style = 'display: none;'
            if (section.className === `main home`) {
                section.style = ''
            }
        })
    } else {
        sections.forEach(section => {
            section.style = 'display: none;'
            if (section.className === `main ${anchor}`) {
                section.style = ''
            }
        })
    }
}


function switchDone(element, id_devoir) {
    let effectuer = element.children[0].getAttribute('data').toLowerCase()
    fetch(`/work/${id_devoir}/${effectuer}`)
    element.children[0].classList.toggle('True')
    element.children[0].classList.toggle('False')
}


function switchWork(element) {
    homeworksContainer.innerHTML = ''
    dates = element.getAttribute('data-action').split('|')
    from = dates[0]
    to = dates[1]
    fromDateObject = new Date()
    fromYear = parseInt(from.split('-')[0])
    fromMonth = parseInt(from.split('-')[1])
    fromDay = parseInt(from.split('-')[2])
    fromDateObject.setFullYear(fromYear, fromMonth, fromDay)
    fromDateString = `${fromDateObject.getFullYear()}-${fromDateObject.getFullMonth()}-${fromDateObject.getFullDay()}`
    toDateObject = new Date()
    toYear = parseInt(to.split('-')[0])
    toMonth = parseInt(to.split('-')[1])
    toDay = parseInt(to.split('-')[2])
    toDateObject.setFullYear(toYear, toMonth, toDay)
    toDateString = `${toDateObject.getFullYear()}-${toDateObject.getFullMonth()}-${toDateObject.getFullDay()}`
    fetch(`/french/${fromDateString}`)
        .then(resp => { return resp.text() })
        .then(frenchFromDate => {
            fetch(`/french/${toDateString}`)
                .then(resp => { return resp.text() })
                .then(frenchToDate => {
                    document.getElementById('worksdates').innerHTML = `<b>${frenchFromDate} - ${frenchToDate}</b>`
                })
        })
    toDateObject = toDateObject.addDays(1)
    toDateString = `${toDateObject.getFullYear()}-${toDateObject.getFullMonth()}-${toDateObject.getFullDay()}`
    currentDateObject = fromDateObject
    currentDateString = `${currentDateObject.getFullYear()}-${currentDateObject.getFullMonth()}-${currentDateObject.getFullDay()}`
    sampleDate = fromDateObject.addDays(1)
    sampleDateString = `${sampleDate.getFullYear()}-${sampleDate.getFullMonth()}-${sampleDate.getFullDay()}`
    console.log(sampleDateString, fromDateString)
    fetch(`/get-previous-and-next-week/${sampleDateString}`)
        .then(response => { return response.json() })
        .then(json => {
            sampleData = json['previous']
            previousWeek = `${sampleData[0]}|${sampleData[sampleData.length - 1]}`
            console.log(previousWeek)
            previousWorkButton.setAttribute('data-action', previousWeek)
            sampleData = json['next']
            nextWeek = `${sampleData[0]}|${sampleData[sampleData.length - 1]}`
            console.log(nextWeek)
            nextWorkButton.setAttribute('data-action', nextWeek)
        })
    while (currentDateString !== toDateString) {
        fetch(`/work/${currentDateString}`)
            .then(response => {
                return response.json()
            })
            .then(json => {
                if (json['matieres'][0]['aFaire'] !== undefined) {
                    homeworksContainer.innerHTML += `
                <div class="column is-full">
                  <b>${json['frenchDate']}</b>
                </div>`
                    json['matieres'].forEach(matiere => {
                        if (matiere['aFaire'] !== undefined) {
                            homeworksContainer.innerHTML += `
                    <div class="column work" onclick="workPopup('${matiere.id}')">
                      <article class="message content">
                        <span class="centered notification"><code>${matiere.matiere}</code></span>
                        <blockquote class="message-body">
                          Evaluation: <i class="fas fa-poll ${matiere.interrogation}"></i>&nbsp;Effectue: <i class="fas fa-check-square ${matiere.aFaire.effectue}"></i>
                          <br>
                        </blockquote>
                      </article>
                    </div>
                    <div class="modal" id="${matiere.id}">
                        <div class="modal-background"></div>
                        <div class="modal-content" style="background-color: #fff; padding: .5em">
                          <h1 class="title">Contenu:</h1>
                          <div class="content">
                            <h2>${matiere.matiere}</h2>
                            ${atob(matiere['aFaire']['contenu'])}
                            <label class="checkbox" onclick="switchDone(this, '${matiere.id}')">
                              Effectué
                              <i class="fas fa-check-square ${matiere.aFaire.effectue}" data="${matiere.aFaire.effectue}"></i>
                            </label>
                            <label class="checkbox">
                              Evaluation
                              <i class="fas fa-poll ${matiere.aFaire.interrogation}"></i>
                            </label>
                          </div>
                        </div>
                        <button class="modal-close is-large" aria-label="close" onclick="workPopup('${matiere.id}')"></button>
                    </div>`
                        }

                    })
                }
            })
        currentDateObject = currentDateObject.addDays(1)
        currentDateString = `${currentDateObject.getFullYear()}-${currentDateObject.getFullMonth()}-${currentDateObject.getFullDay()}`
    }
}

