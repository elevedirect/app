const sections = document.querySelectorAll('.main')
const actions = document.querySelectorAll('.data-action')
let dataAction

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
    await navigator.share({'url': 'http://eleve-direct.server.camarm.fr', 'text': 'Moyennes, carte de cantine et plus en core avec Eleve Direct !', 'title': 'Rejoins Eleve Direct !'})
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
