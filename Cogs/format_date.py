class FormatDate():
    def __init__(self, date) -> None:
        self.date = date

    def format_date(self):
        sent_date = self.date[:4] + '/' + self.date[4:6] + '/' + self.date[6:8]
        return sent_date
