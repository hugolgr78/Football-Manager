import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.util_functions import knockout_draw

class CupDraw(ctk.CTkFrame):
    def __init__(self, parent, cup_id):
        """
        A frame that displays the cup draw.

        Args:
            parent (ctk.CTkFrame): The parent frame where the cup draw will be placed.
            cup_id (int): The ID of the cup for which the draw is displayed.
        """

        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)
        
        self.parent = parent
        self.cup_id = cup_id
        self.pack(fill = "both", expand = True)
        self.update_idletasks()
        
        self.startDraw()
        self.finishDraw()

    def startDraw(self):
        """
        Starts the cup draw process.
        """

        self.cup = Cup.get_cup_by_id(self.cup_id)
        self.teams = CupTeams.get_teams_by_cup(self.cup_id)
        self.matches = Matches.get_cup_matches_by_round(self.cup_id, self.cup.current_round)

        self.qualified = []
        
        for team in self.teams:
            league = LeagueTeams.get_league_by_team(team.team_id).league_id
            if League.calculate_league_depth(league) < 2:
                self.qualified.append(team.team_id)

        self.qualified.extend(CupTeams.get_qualified_from_groups(self.cup))

    def finishDraw(self):
        """
        Finalizes the cup draw.
        """
        
        self.pack_forget()