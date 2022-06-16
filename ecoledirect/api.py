
class Route:

    def __init__(self, path, args):
        self._path = path
        self._args = args

    @property
    def path(self):
        return self._path

    @property
    def args(self):
        return self._args


login_args = 'v=4.14.4'
LOGIN = Route('login.awp', login_args)
notes_args = 'verbe=get&v=4.14.4'
NOTES = Route('eleves/%s/notes.awp', notes_args)
work_args = 'verbe=get&v=4.14.4'
WORK = Route('Eleves/%s/cahierdetexte.awp', work_args)
date_work_args = 'verbe=get&v=4.14.4'
DATE_WORK = Route('Eleves/%s/cahierdetexte/%s.awp', date_work_args)
done_work_args = 'verbe=put&v=4.14.5'
DONE_WORK = Route('Eleves/%s/cahierdetexte.awp', done_work_args)
