from threading import Thread



class Parsing(Thread):
    def __init__(self, website_object):
        super().__init__()
        self.website_object = website_object
        self.events = []

    def parsing(self):
        self.events = self.website_object.get_events()

    def run(self):
        while True:
            self.parsing()


parsing = Parsing()
parsing.start()
