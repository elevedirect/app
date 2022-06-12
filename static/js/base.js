const sections = document.querySelectorAll('.main')
const actions = document.querySelectorAll('.data-action')
const homeworksContainer = document.getElementById('homeworks-container')
const nextWorkButton = document.getElementById('nextwork')
const previousWorkButton = document.getElementById('previouswork')
let dataAction, dates, from, to, fromDateObject, fromYear, fromMonth, fromDay, fromDateString, toDateObject, toYear,
    toMonth, toDay, toDateString, currentDateObject, currentDateString, sampleDate, previousWeek, nextWeek
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

function expand(periode) {
    document.getElementById(periode).classList.toggle('active')
    document.getElementById(periode + 'icon').classList.toggle('active')
}

async function share() {
    await navigator.share({
        'url': 'http://eleve-direct.server.camarm.fr',
        'text': 'Moyennes, carte de cantine et plus en core avec Eleve Direct !',
        'title': 'Rejoins Eleve Direct !'
    })
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
                        homeworksContainer.innerHTML += `
                    <div class="column work">
                      <article class="message content">
                        <span class="centered notification"><code>${matiere.matiere}</code></span>
                        <blockquote class="message-body">
                          Evaluation: <i class="fas fa-poll ${matiere.interrogation}"></i>&nbsp;Effectue: <i class="fas fa-check-square ${matiere.aFaire.effectue}"></i>
                          <br>
                        </blockquote>
                      </article>
                    </div>`
                    })
                }
            })
        currentDateObject = currentDateObject.addDays(1)
        currentDateString = `${currentDateObject.getFullYear()}-${currentDateObject.getFullMonth()}-${currentDateObject.getFullDay()}`
    }
    sampleDate = toDateObject.addDays(6)
    nextWeek = `${toDateString}|${sampleDate.getFullYear()}-${sampleDate.getFullMonth()}-${sampleDate.getFullDay()}`
    sampleDate = fromDateObject.removeDays(6)
    fromDateObject = fromDateObject.removeDays(1)
    fromDateString = `${fromDateObject.getFullYear()}-${fromDateObject.getFullMonth()}-${fromDateObject.getFullDay()}`
    previousWeek = `${sampleDate.getFullYear()}-${sampleDate.getFullMonth()}-${sampleDate.getFullDay()}|${fromDateString}`
    previousWorkButton.setAttribute('data-action', previousWeek)
    nextWorkButton.setAttribute('data-action', nextWeek)
}
