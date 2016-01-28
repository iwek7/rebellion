from agents import Agent, Cop, Citizen
import pandas as pd

# tworzy tabele z danymi do dalszej analizy

class StatisticsOffice():

    def __init__(self, simulation_id = 1):
        """Inicjacja struktur przechowujacych dane."""

        self.column_names = ["simulation_id",
                             "period_id", 
                             "citizen_id", 
                             "citizen_type",
                             "x_location",
                             "y_location",
                             "is_prisoner",
                             "sentence_total",
                             "sentence_left",
                             "made_arrest",
                             "vision_range",
                             "risk_aversion",
                             "grievance",
                             "perceived_hardship",
                             "rebel_threshold"]
        
        self.summary_statistics = pd.DataFrame(columns = self.column_names)
        
              
    def log_citizen(self, agent, period_id):
        """ Adds citizen data to final table"""
        data = [
                1,                      # simulation_id
                period_id,              # period_id
                agent.id,               # citizen_id
                agent.my_type,          # citizen_type
                agent.location[0],      # x_location
                agent.location[1],      # y_location
                agent.jailed,           # is_prisoner
                agent.sentence_total,   # sentence_total
                agent.sentence_left,    # sentence_left
                agent.made_arrest,      # made_arrest
                agent.vision_range,     # vision_range
                agent.risk_aversion,
                agent.grievance,
                agent.perceived_hardship,
                agent.rebel_threshold
            ] 

        
        self.summary_statistics.loc[len(self.summary_statistics)] = data

   
    def export_data(self, path):
        #try:
        self.summary_statistics.to_csv(path, cols = self.column_names)
        #except Exception:
        #    print("Export failed.")
        #    return False