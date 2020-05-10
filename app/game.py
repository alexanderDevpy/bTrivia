

class Game():
    def __init__(self,room):
        self.room = room
        self.sokid = []
        self.gameround = 1
        self.questions = []
        self.speed = []
        self.count = 0
        self.rasp = 0
        self.corans = []
        self.users = 3





    def updateuser(self,user,sockid):


        if len(self.sokid) == 0:
            self.sokid.append(('red',sockid,user))
        elif len(self.sokid) == 1:
            self.sokid.append(('blue', sockid,user))
        else:
            self.sokid.append(('green', sockid,user))


