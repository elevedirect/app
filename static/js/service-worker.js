self.addEventListener('install', (evt) => {
    console.log('Elevedirect Installed')
});


self.addEventListener('periodicsync', function(event) {
    if (event.tag === 'notifs') {
        event.waitUntil(getNotifications())
    }
})


async function getNotifications() {
    var notif
    fetch('/get-notifs')
        .then(resp => resp.json())
        .then(data => {
            for (const notif_data of data.data) {
                notif = new Notification(notif_data.title, {"body": notif_data.body, "icon": notif_data.icon})
                notif.addEventListener('click', () => {
                    notif.close()
                })
            }
            console.log(data)
        })
}

window.setInterval(getNotifications, 5 * 60 * 1000)