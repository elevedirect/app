const sections = document.querySelectorAll('.main')
const actions = document.querySelectorAll('.data-action')
const homeworksContainer = document.getElementById('homeworks-container')
const nextWorkButton = document.getElementById('nextwork')
const previousWorkButton = document.getElementById('previouswork')
let loader = document.querySelector('.eloader')
let dataAction, dates, from, to, fromDateObject, fromYear, fromMonth, fromDay, fromDateString, toDateObject, toYear,
    toMonth, toDay, toDateString, currentDateObject, currentDateString, sampleDate, previousWeek, nextWeek, sampleDateString,
    sampleData, content, footer, description, homework_content, seance_content, docs, seance_docs
var html, order


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
    let month = (date.getMonth() + 1).toString()
    return ("0" + month).slice(-2);
}

Date.prototype.getFullDay = function () {
    let date = new Date(this.valueOf());
    let day = date.getDate().toString()
    return ("0" + day).slice(-2);
}

var active_section = 'home'
var all_sections = []

function changeSectionTo(section_name) {
    sections.forEach(section => {
        section.style = 'display: none;'
        if (section.className === `main ${section_name}`) {
            section.style = ''
        }
    })
}

actions.forEach(action => {
    all_sections.push(action.getAttribute('data-action'))
    action.addEventListener('click', () => {
        dataAction = action.getAttribute('data-action')
        active_section = dataAction
        changeSectionTo(dataAction)
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
        active_section = anchor
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
    let next_attr = ''
    if (effectuer === 'false') {
        next_attr = 'True'
    } else {
        next_attr = 'False'
    }
    element.children[0].setAttribute('data', next_attr)
}

function homeworkTab(el, style_1, style_2, homework, tab) {
    el.classList.add('is-active')
    document.querySelector(`[tabs_data="${homework}${tab}"]`).classList.remove('is-active')
    document.getElementById(`${homework}_devoirs`).style = style_1
    document.getElementById(`${homework}_seance`).style = style_2
}

async function processHomeworkChangement(element) {
    homeworksContainer.innerHTML = ''
    dates = element.getAttribute('data-action').split('|')
    from = dates[0]
    to = dates[1]
    fromDateObject = new Date()
    fromYear = parseInt(from.split('-')[0])
    fromMonth = parseInt(from.split('-')[1]) - 1
    fromDay = parseInt(from.split('-')[2])
    fromDateObject.setFullYear(fromYear, fromMonth, fromDay)
    fromDateString = `${fromDateObject.getFullYear()}-${fromDateObject.getFullMonth()}-${fromDateObject.getFullDay()}`
    toDateObject = new Date()
    toYear = parseInt(to.split('-')[0])
    toMonth = parseInt(to.split('-')[1]) - 1
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
    currentDateObject = fromDateObject
    currentDateString = `${currentDateObject.getFullYear()}-${currentDateObject.getFullMonth()}-${currentDateObject.getFullDay()}`
    sampleDate = fromDateObject.addDays(1)
    sampleDateString = `${sampleDate.getFullYear()}-${sampleDate.getFullMonth()}-${sampleDate.getFullDay()}`
    fetch(`/get-previous-and-next-week/${sampleDateString}`)
        .then(response => { return response.json() })
        .then(json => {
            sampleData = json['previous']
            previousWeek = `${sampleData[0]}|${sampleData[sampleData.length - 1]}`
            previousWorkButton.setAttribute('data-action', previousWeek)
            sampleData = json['next']
            nextWeek = `${sampleData[0]}|${sampleData[sampleData.length - 1]}`
            nextWorkButton.setAttribute('data-action', nextWeek)
        })
    while (currentDateString !== toDateString) {
        await fetch(`/work/${currentDateString}`)
            .then(response => {
                return response.json()
            })
            .then(json => {
                if (json['homeworks'].length > 0) {
                    html = ''
                    html += `
                    <div data-order="${json.date.replaceAll('-', '')}">
                        <div class="column is-full">
                          <b>${json['frenchDate']}</b>
                        </div>
                    `
                    json['homeworks'].forEach(matiere => {
                        description = ''
                        homework_content = ''
                        seance_content = ''
                        docs = ''
                        seance_docs = ''
                        footer = ''

                        if (matiere.has_homework) {
                            description += `Evaluation: <i class="fas fa-poll ${matiere.interrogation}"></i>&nbsp;Effectue: <i class="fas fa-check-square ${matiere.aFaire.effectue}"></i>`
                            if (matiere.has_documents) {
                                docs += ' <h3>Documents:</h3>'
                                matiere.documents.forEach(doc => {
                                    docs += `
                                    <span class="tag is-normal is-a-link"><a href="${doc.url}" download="${doc.name}">${doc.name}</a></span>
                                    `
                                })
                            }
                            homework_content = matiere.contenu
                            footer = `
                            <label class="checkbox" onclick="switchDone(this, '${matiere.id}')">
                              Effectué
                              <i class="fas fa-check-square ${matiere.effectue}" data="${matiere.effectue}"></i>
                            </label>
                            <label class="checkbox">
                              Evaluation
                              <i class="fas fa-poll ${matiere.interrogation}"></i>
                            </label>
                            `
                        }

                        if (matiere.has_seance) {
                            description += `<p style="margin-bottom: 0;">Contenu de séance <i class="fas fa-users-class"></i></p>`
                            if (matiere.seance.has_documents) {
                                docs += ' <h3>Documents:</h3>'
                                matiere.seance.documents.forEach(doc => {
                                    docs += `
                                <span class="tag is-normal is-a-link"><a href="${doc.url}" download="${doc.name}">${doc.name}</a></span>
                                `
                                })
                            }
                            seance_content = matiere.seance.contenu
                        }

                        content =  `
                        <div id="${matiere.id}_devoirs">
                          ${homework_content}
                          ${docs}
                        </div>
                        <div id="${matiere.id}_seance" style="display: none">
                          ${seance_content}
                          ${seance_docs}
                        </div>
                        ${footer}
                        `

                        html += `
                        <div class="column work" onclick="workPopup('${matiere.id}')">
                          <article class="message content">
                            <span class="centered notification"><code>${matiere.matiere}</code></span>
                            <blockquote class="message-body">
                              ${description}
                            </blockquote>
                          </article>
                        </div>
                        <div class="modal" id="${matiere.id}">
                            <div class="modal-background"></div>
                            <div class="modal-content" style="background-color: #fff; padding: 1em; width: 97%; border-radius: 15px">
                              <h1 class="title">Contenu:</h1>
                              <div class="content">
                                <h2>${matiere.matiere}</h2>
                                <div class="tabs is-centered is-full">
                                  <ul>
                                    <li class="is-active" tabs_data="${matiere.id}0" onclick="homeworkTab(this, '', 'display: none', '${matiere.id}', '1')">
                                      <a>
                                        <span class="icon is-small"><i class="fas fa-ruler" aria-hidden="true"></i></span>
                                        <span>Devoirs</span>
                                      </a>
                                    </li>
                                    <li tabs_data="${matiere.id}1" onclick="homeworkTab(this, 'display: none', '', '${matiere.id}', '0')">
                                      <a>
                                        <span class="icon is-small"><i class="fas fa-users-class" aria-hidden="true"></i></span>
                                        <span>Contenu de séance</span>
                                      </a>
                                    </li>
                                  </ul>
                                </div>
                                ${content}
                              </div>
                            </div>
                            <button class="modal-close is-large" aria-label="close" onclick="workPopup('${matiere.id}')"></button>
                        </div>`
                    })
                    html += '</div>'
                    homeworksContainer.innerHTML += html
                }
            })
        currentDateObject = currentDateObject.addDays(1)
        currentDateString = `${currentDateObject.getFullYear()}-${currentDateObject.getFullMonth()}-${currentDateObject.getFullDay()}`
    }
}

async function switchWork(element) {
    processHomeworkChangement(element).then(() => {
        sortHomeworks()
    })
}

function sortHomeworks() {
    homeworks = Array.from(homeworksContainer.querySelectorAll('div[data-order]'))
    sorted = homeworks.sort((a, b) => {
        if (parseInt(a.getAttribute('data-order')) > parseInt(b.getAttribute('data-order'))) {
            return 1
        }
        if (parseInt(a.getAttribute('data-order')) < parseInt(b.getAttribute('data-order'))) {
            return -1
        }
        return 0
    })
    homeworksContainer.innerHTML = ''
    sorted.forEach(el => {
        homeworksContainer.appendChild(el)
    })
}

function loaderStart() {
    loader.classList.remove('unactive')
}

function loaderStop() {
    loader.classList.remove('unactive')
    setTimeout(() => {
        loader.classList.add('unactive')
    }, 500)
}

window.addEventListener('beforeunload', loaderStart)
window.addEventListener('load', loaderStop)
