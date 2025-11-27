class Structure:
# constructor
    def __init__(self):
        self.before_target = []
        self.target = []
        self.next_target = []
        self.distance = 0
        self.cost = 0
# prev
    def setBeforeTarget(self, before_target):
        self.before_target = before_target
    
    def getBeforeTarget(self):
        return self.before_target
# target
    def setTarget(self, target):
        self.target = target

    def getTarget(self):
        return self.target
# next
    def setNextTarget(self, next_target, append_list=False):
        if append_list:
            self.next_target.append(next_target)
        else:
            self.next_target = next_target

    def getNextTarget(self):
        return self.next_target
# distance
    def setDistance(self, distance):
        self.distance = distance
    
    def getDistance(self):
        return self.distance
# cost
    def setCost(self, cost):
        self.cost = cost
    
    def getCost(self):
        return self.cost