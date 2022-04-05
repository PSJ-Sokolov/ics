import random
from mesa import Agent

class Cell(Agent):
    '''Description of the grid points of the CA'''

    # Definitions of state variables    #Not used?
    Susceptible = 1
    Infected = 2
    Recovered = 3
    
    #TO BE CHECKED: States are never empty, so should the next properties be zero anyway?
    #See model.py for reference
    def __init__(self,pos,model,init_state=0):
        '''Create cell in given x,y position, with given initial state'''
        super().__init__(pos,model)
        self.x,self.y = pos
        self.state = init_state
        self.timecounter = 0
        self.inf = 0.0              
        self.infduration = 0
        self.immduration = 0
        self._nextstate = None
        self._nextinf = None
        self._nextinfduration = None
        self._nextimmduration = None

    def step(self):
        '''Compute the next state of a cell'''
        # Assume cell is unchanged, unless something happens below
        self._nextinf = self.inf
        self._nextinfduration = self.infduration
        self._nextimmduration = self.immduration
        self._nextstate = self.state
        
        # No empty space in our model
        # Empty squares - potential reproduction of susceptibles
        # No reproduction
        #if self.state == 0:
        #   Susneighbors = 0
        #   neis = self.model.grid.get_neighbors((self.x, self.y), moore=True, include_center=False)
        #   for nei in neis:
        #       if nei.state == self.Susceptible:
        #            Susneighbors += 1
        #    if Susneighbors > 0:
        #        if random.random() < self.model.r*Susneighbors:
        #            self._nextstate = self.Susceptible

        # Susceptibles - might get infected
        if self.state == self.Susceptible:
            # Natural death
            #if random.random() < self.model.d:
            #if False:
            #    self._nextstate = 0
            # Infection?
            #else:
            neis = self.model.grid.get_neighbors((self.x, self.y), moore=True, include_center=False)
            tot_inf = 0.0
            for nei in neis:
                if nei.state == self.Infected:
                    tot_inf += nei.inf
            infprob = 0.0
            if tot_inf > 0:
                infprob = tot_inf / (tot_inf + self.model.h_inf)
            if random.random() < infprob:
                self._nextstate = self.Infected
                # Inherit infectivity of one infecting neighbour
                infprobsum = 0.0
                rand = random.uniform(0, tot_inf)
                for nei in neis:
                    if nei.state == self.Infected:
                        infprobsum += nei.inf
                        if rand < infprobsum:
                            # Inherit pathogen characteristics from infecting neighbour
                            self._nextinf = nei.inf
                            self._nextinfduration = nei.infduration
                            self._nextimmduration = nei.immduration
                            break

        # Infected - might die naturally or die after disease_duration
        #Becomr R instead Empty
        #elif self.state == self.Infected:
        #    # Natural death or death by disease
        #    if random.random() < self.model.d or self.timecounter > self.infduration:
        #        self._nextstate = 0
        #        self._nextinf = 0.0
        #        self._nextinfduration = 0
        #        self.timecounter = 0
        #    # Else count how long it has been ill and apply potential mutations
        #    else:
        #        self.timecounter += 1

        # Infected - recover after disease_duration
        elif self.state == self.Infected:
            if  self.timecounter > self.infduration:
                self._nextstate = self.Recovered
                self._nextinf = 0.0
                self._nextinfduration = 0 
                self.timecounter = 0
            # Else count how long it has been ill and apply potential mutations     #Mutation should be add here
            else:
                self.timecounter += 1
                mu=0.4                                  #Mutation probability
                rand=random.random()
                if rand<mu*0.5:
                    self._nextinfduration += 1          #Mutation to more infectivity duration
                elif rand<mu:
                    self._nextinfduration -= 1          #Mutation to less infectivity duration
                
        # Recovered - lose immunity after immunity_duration
        elif self.state == self.Recovered:
            if  self.timecounter > self.immduration:
                self._nextstate = self.Susceptible
                self._nextinf = 0.0
                self._nextinfduration = 0 #It should be already zero
                self._nextimmduration = 0
                self.timecounter = 0
            # Else count how long it has been recovered and apply potential mutations     #Mutation should be add here
            else:
                self.timecounter += 1                        
                
    def advance(self): 
        self.state = self._nextstate
        self.inf = self._nextinf
        self.infduration = self._nextinfduration
        self.immduration = self._nextimmduration
