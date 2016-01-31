
#import os
#os.chdir('C:\scisoft\workspace\Rebellion')


from agents import Cop, Citizen, Agent


import random
import math
import matplotlib.pyplot as plt
import numpy as np
from statisticsOffice import StatisticsOffice
from gridplot import GridPlot
import pandas as pd

# Model Rebellion
# http://ccl.northwestern.edu/netlogo/models/Rebellion
# autorzy kodu:
# Michal Iwanczuk 53104


# OPIS:
# This project models the rebellion of a subjugated population 
# against a central authority. It is is an adaptation of Joshua 
# Epstein's model of civil violence (2002).

# The population wanders around randomly. 
# If their level of grievance against the central 
# authority is high enough, and their perception of the risks
# involved is low enough, they openly rebel. A separate population of 
# police officers ("cops"), acting on behalf of the central authority, 
# seeks to suppress the rebellion. The cops wander around randomly and 
# arrest people who are actively rebelling.

class Government():
    """
    Rzad kontroluje panstwo i jego policje (agentow typu Cop)
    Rzad chce sie za wszelka cene utrzymac przy wladzy i rozkazuje 
    policjata aresztowac obywateli (agentow typu Citizen).
    Wizerunek rzadu ma wplyw na sklonnosc 
    do przechodzenia Citizenow do stanu rebel.
    Do kometencji rzadu nalezy ustanawianie zasad dzialania policji.

    """
    def __init__(self, legitimacy):
        """Inicjacja zasad ustalanych przez rzad i jego charakterystyk."""

        # wspolczynnik poparcia rzadu w spoleczenstwie
        # waha sie od 0 do 1
        assert(legitimacy >= 0 and legitimacy <= 1)
        self.legitimacy = legitimacy
        # czasy wyrokow odpowiednio dla winnych aresztowanych
        # wyroki sa losowane z rozkladu jednostajnego
        self.rebel_jail_time = range(0, 30)

class Prison():
    """Klasa odpowiadajaca za przetrzymywanie wiezniow"""
    def __init__(self):
        self.prisoners = []

    def get_leaving_prisoners(self, record_data = False):
        """
        Usuwa wiezniow, ktorych wyrok uplunal z wiezienia i zwraca ich w liscie.
        Uwaga! Jesli nie zostana oslozeni przez 
        obiekt odbierajacy te liste to znikna.
        """
        prisoners_to_go = []
        # iteracja od tylu poniewaz usuwamy elementy w taki a nie innyc sposob
        for i in reversed(range(len(self.prisoners))): 
            # zmniejszenie wyroku
            self.prisoners[i].sentence_left -= 1  
            if self.prisoners[i].sentence_left <= 0:
                self.prisoners[i].jailed = False

                # to na potrzeby zbierania statystyk 
                self.prisoners[i].sentence_left = 0
                self.prisoners[i].sentence_total = 0

                self.prisoners[i].my_type = self.prisoners[i].agent_type["PassiveCitizen"]
                prisoners_to_go.append(self.prisoners[i])

                del self.prisoners[i]
            else:
                if record_data:
                    self.prisoners[i].record_data()
        return prisoners_to_go

class Country():
    """
    Panstwo, przestrzen w ktorej zyja agenci. 
    Wladze w panstwie sprawoje rzad.
    """
    def __init__(self, dimension, num_citizens, num_cops, max_iterations):
        """
        Inicjacja przestrzeni panstwa wraz z rzadem, losowymi
        Citizenami i Copami

        """
        self.government = Government(.82)
        self.prison = Prison()
        # self.statistics_office = StatisticsOffice()
        # lista pol zajetych
        # tuple : referencja do obiektu
        # inicjalizacja pustej przestrzeni
        self.occupied_fields = dict()
        for x in range(dimension):
            for y in range(dimension):
                self.occupied_fields[(x,y)] = None
        # dimension * dimension to ilosc pol
        self.dimension = dimension

        # ilosc agentow typu citizen
        self.num_citizens = num_citizens
        # ilosc obywateli typu Cop
        self.num_cops = num_cops
        # ilosc iteracji symulacji
        self.max_iterations = max_iterations
      
        
        # zmienne do wizualizacji symulacji
        self.plot_data = np.zeros((self.dimension,self.dimension))


        self.id_generator =  self.create_id_generaor(start_id = 1)

        # kolekcjonowanie danych symulacji
        self._column_names = [
                             "number_of_agents", 
                             "number_of_arrests", # tylko dla copa uzupelniane
                             "total_grievance",
                             "total_preceived_hardship",
                             "total_risk_aversion"                       
                             ]
        self.statistics = {
                           0 : pd.DataFrame(columns = self._column_names),
                           1 : pd.DataFrame(columns = self._column_names),
                           2 : pd.DataFrame(columns = self._column_names),
                           3 : pd.DataFrame(columns = self._column_names),
                           4 : pd.DataFrame(columns = self._column_names)
                           }

        
        self.agent_types = {"None": 0 ,
                            "ActiveCitizen" : 1, 
                            "PassiveCitizen" : 2,
                            "Cop" : 3,
                            "Prisoner" : 4
                            }


    def get_free_location(self, search_for_nones = False):
        """Zwraca wolna lokalizacje."""
        if search_for_nones :
            free_fields = [field for field in self.occupied_fields 
                            if self.occupied_fields[field] == None]
        else:
            free_fields = [field for field in self.occupied_fields 
                            if self.occupied_fields[field].my_type == 0]
            
        assert(len(free_fields) > 0)
        return random.choice(free_fields)

    def update_plot_data(self):
        # agent w tej iteracji to tuple
        # dodajemy
        for x in range(self.dimension):
            for y in range(self.dimension):
                    self.plot_data[(x,y)] = self.occupied_fields[(x,y)].my_type


    def create_id_generaor(self, start_id = 1):
        i = start_id
        while True:
            yield i
            i += 1

    def plot(self):
        """Metoda odpowiedzialna za wizualizacje modelu."""    
        self.update_plot_data()
        self.gp.plot()
    
    def initialize_simulation(self, visualize):
        """ Metoda odpowiedzialna za inicjalizacje srodowiska symulacji """
        for i in range(self.num_citizens):
            Citizen(self, next(self.id_generator))
        for i in range(self.num_cops):
            Cop(self, next(self.id_generator))

        # reszte pol wypelnic agentami typu none
        for location in self.occupied_fields: 
            if self.occupied_fields[location] == None:
                Agent(self, -1 , location)
        if visualize:
            self.update_plot_data()
            self.gp = GridPlot(self.plot_data,["white","red", "green", "black"])
        
    
    def export_statistics(self, path, agents_to_export = list()):
        """
            Eksportowanie statystyk agentow do pliku csv zadanego w zmiennej path
            mozemy przekazac liste nazw agentow , ktorych statystyki chcemy
            defaultowo bierzemy wszystko
        """

        if len(agents_to_export) <= 0: 
            agents_to_export = list((self.agent_types.keys()))
            agents_to_export.remove('None')
        # sprawdzenie czy lista agentow jest niepusta i czy podani agenci istnieja
        assert(set(agents_to_export).issubset(set(self.agent_types.keys())))
        export_cols = ["agent_type"] + self._column_names
        df_to_export = pd.DataFrame(columns = export_cols)
        # do kazdego dataframe ze statystykami dopisuje kolumne wypelniona rodzajem agenta
        # wszystkie dataframy skladam w jeden i potem eksportuje
        for agent_type in agents_to_export:
            temp_df = self.statistics[self.agent_types[agent_type]]
            temp_df["agent_type"] = [agent_type for i in range(len(temp_df))]
            df_to_export = pd.concat([df_to_export, temp_df])
        
        df_to_export.to_csv(path, columns = export_cols)
            
                                     
    def run(self, record_data = False, visualize = False):
        """
        Metoda odpowiedzialna za przeprowadzenie symulacji 
        """
        self.initialize_simulation(visualize)

        for i in range(self.max_iterations):

            # dodanie nowego wiersza z danymi z zerami
            if record_data:
                for key, dataframe in self.statistics.items():
                    dataframe.loc[len(dataframe)] = (
                        [0 for stat in range(len(self._column_names))])

            # obsluzenie wiezienia
            freed_prisoners = self.prison.get_leaving_prisoners(record_data)
            # umieszczenie wolnych citizenow na dostepnych polach
            for prisoner in freed_prisoners:
                prisoner.location = self.get_free_location()
                self.occupied_fields[prisoner.location] = prisoner
                           
            for agent in self.occupied_fields:
                if self.occupied_fields[agent].my_type != 0:
                    ag = self.occupied_fields[agent]
                    ag.update_agent(record_data)
                          
            if visualize:
                self.plot()

            print(i)
            

dim = 30
frac_cops = 0.04
frac_citizens = 0.7
c = Country(
        dim, 
        math.floor(frac_citizens * dim * dim), 
        math.floor(frac_cops * dim * dim), 
        5
        )
c.run(record_data = False, visualize = False)
# c.export_statistics(path = "C:/Users/Michal/Documents/Visual Studio 2013/Projects/Rebellion/Rebellion/data.csv")


