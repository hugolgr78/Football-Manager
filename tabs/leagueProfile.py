import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image
import io
from utils.frames import LeagueTable, MatchdayFrame
from utils.playerProfileLink import PlayerProfileLink

class LeagueProfile(ctk.CTkFrame):
    def __init__(self, parent, session, manager_id, changeBackFunction = None):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.session = session
        self.manager_id = manager_id
        self.changeBackFunction = changeBackFunction

        self.team = Teams.get_teams_by_manager(self.session, self.manager_id)[0]
        self.leagueTeams = LeagueTeams.get_league_by_team(self.session, self.team.id)
        self.league = League.get_league_by_id(self.session, self.leagueTeams.league_id)

        self.profile = Profile(self, self.session, self.league)
        self.matchdays = None
        self.graphs = None
        self.history = None
        self.titles = ["Profile", "Matchdays", "Graphs", "History"]
        self.tabs = [self.profile, self.matchdays, self.graphs, self.history]
        self.classNames = [Profile, Matchdays, Graphs, History]

        self.activeButton = 0
        self.buttons = []

        self.tabsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 50, corner_radius = 0)
        self.tabsFrame.pack(expand = True, fill = "both", padx = 10, pady = 10)

        self.createTabs()
        self.profile.pack(expand = True, fill = "both")

    def createTabs(self):

        self.buttonHeight = 40
        self.buttonWidth = 200
        self.button_background = TKINTER_BACKGROUND
        self.hover_background = GREY_BACKGROUND
        self.gap = 0.102

        gapCount = 0
        for i in range(len(self.tabs)):
            button = ctk.CTkButton(self.tabsFrame, text = self.titles[i], font = (APP_FONT, 20), fg_color = self.button_background, corner_radius = 0, height = self.buttonHeight, width = self.buttonWidth, hover_color = self.hover_background)
            button.place(relx = self.gap * gapCount, rely = 0, anchor = "nw")
            button.configure(command = lambda i = i: self.changeTab(i))
            
            gapCount += 2
            self.buttons.append(button)
            self.canvas(6, 55, self.gap * gapCount - 0.005)

        self.buttons[self.activeButton].configure(state = "disabled")

        ctk.CTkCanvas(self.tabsFrame, width = 1220, height = 5, bg = APP_BLUE, bd = 0, highlightthickness = 0).place(relx = 0, rely = 0.82, anchor = "w")

        if self.changeBackFunction:
            backButton = ctk.CTkButton(self.tabsFrame, text = "Back", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND, corner_radius = 5, height = self.buttonHeight - 10, width = 100, hover_color = CLOSE_RED, command = lambda: self.changeBackFunction())
            backButton.place(relx = 0.975, rely = 0, anchor = "ne")

    def canvas(self, width, height, relx):
        canvas = ctk.CTkCanvas(self.tabsFrame, width = width, height = height, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = relx, rely = 0, anchor = "nw")

    def changeTab(self, index):
        self.buttons[self.activeButton].configure(state = "normal")
        self.tabs[self.activeButton].pack_forget()
        
        self.activeButton = index
        self.buttons[self.activeButton].configure(state = "disabled")

        if not self.tabs[self.activeButton]:
            self.tabs[self.activeButton] = globals()[self.classNames[self.activeButton].__name__](self, self.session, self.league)

        self.tabs[self.activeButton].pack()

class Profile(ctk.CTkFrame):
    def __init__(self, parent, session, league):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.session = session
        self.league = league

        src = Image.open(io.BytesIO(self.league.logo))
        src.thumbnail((100, 100))
        self.logo = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(self, image = self.logo, text = "", fg_color = TKINTER_BACKGROUND).place(relx = 0.08, rely = 0.1, anchor = "center")

        ctk.CTkLabel(self, text = f"{self.league.name} - {self.league.year}", font = (APP_FONT_BOLD, 30), fg_color = TKINTER_BACKGROUND).place(relx = 0.15, rely = 0.1, anchor = "w")

        self.tableFrame = LeagueTable(self, 480, 600, 0.03, 0.2, GREY_BACKGROUND, "nw", corner_radius = 15, highlightManaged = True)
        self.tableFrame.defineManager(self.session, self.parent.manager_id)
        self.tableFrame.addLeagueTable()

        self.statsFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 310, height = 480, corner_radius = 15)
        self.statsFrame.place(relx = 0.65, rely = 0.2, anchor = "nw")
        self.pack_propagate(False)

        self.addStats()

    def addStats(self):
        ctk.CTkLabel(self.statsFrame, text = "Stats", font = (APP_FONT_BOLD, 30), fg_color = GREY_BACKGROUND).pack(pady = 10)

        self.topScorers = MatchEvents.get_all_goals(self.session, self.league.id)
        self.topAssisters = MatchEvents.get_all_assists(self.session, self.league.id)
        self.topCleanSheets = MatchEvents.get_all_clean_sheets(self.session, self.league.id)
        self.mostYellowCards = MatchEvents.get_all_yellow_cards(self.session, self.league.id)
        self.bestAverageRatings = TeamLineup.get_all_average_ratings(self.session, self.league.id)

        self.stats = [self.topScorers, self.topAssisters, self.topCleanSheets, self.mostYellowCards, self.bestAverageRatings]
        self.statNames = ["Top Scorer", "Top Assister", "Most Clean Sheets", "Most Yellow Cards", "Best Average Rating"]

        expandedImage = Image.open("Images/expand.png")
        expandedImage.thumbnail((30, 30))
        self.expandEnabled = ctk.CTkImage(expandedImage, None, (expandedImage.width, expandedImage.height))

        for stat, statName in zip(self.stats, self.statNames):
            
            frame = ctk.CTkFrame(self.statsFrame, fg_color = GREY_BACKGROUND, width = 280, height = 75, corner_radius = 15)
            frame.pack(pady = 5, padx = 5)

            expandButton = ctk.CTkButton(frame, text = "", image = self.expandEnabled, fg_color = GREY_BACKGROUND, corner_radius = 0, height = 30, width = 30, hover_color = GREY_BACKGROUND)
            expandButton.place(relx = 0.98, rely = 0.7, anchor = "e")

            if not stat:
                stat = [(0, "N/A", "N/A", 0)]
                expandButton.configure(image = None, state = "disabled")
            else:
                stat = stat[:5]
                expandButton.configure(command = lambda stat = stat, statName = statName: self.expandStats(stat, statName)) 

            ctk.CTkLabel(frame, text = statName, font = (APP_FONT_BOLD, 25), fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.15, anchor = "w")

            if stat[0][0] == 0:
                ctk.CTkLabel(frame, text = "N/A", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.7, anchor = "w")
            else:
                # ctk.CTkLabel(frame, text = str(stat[0][1] + " " + stat[0][2]), font = (APP_FONT, 15) if len(str(stat[0][1] + " " + stat[0][2])) > 15 else (APP_FONT, 20), fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.7, anchor = "w")
                player = Players.get_player_by_name(self.session, str(stat[0][1]), str(stat[0][2]))
                PlayerProfileLink(frame, self.session, player, str(stat[0][1] + " " + stat[0][2]), "white", 0.05, 0.7, "w", GREY_BACKGROUND, self.parent)

            ctk.CTkLabel(frame, text = round(stat[0][3], 2), font = (APP_FONT, 20), fg_color = GREY_BACKGROUND).place(relx = 0.75, rely = 0.7, anchor = "center")

    def expandStats(self, stats, statName):
        pass

class Matchdays(ctk.CTkFrame):
    def __init__(self, parent, session, league):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.session = session
        self.league = league
        self.currentMatchday = self.league.current_matchday

        self.frames = []
        self.activeFrame = self.currentMatchday - 1

        self.numTeams = self.parent.leagueTeams.get_teams_by_league(self.session, self.league.id)
        self.numMacthdays = len(self.numTeams) * 2 - 2

        self.buttonsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 980, height = 60, corner_radius = 15)
        self.buttonsFrame.place(relx = 0, rely = 0.98, anchor = "sw")

        self.createFrames()
        self.addButtons()

    def createFrames(self):
        for i in range(self.numMacthdays):
            if i == self.currentMatchday - 1:
                matchday = Matches.get_matchday_for_league(self.session, self.league.id, self.currentMatchday)
                frame = MatchdayFrame(self, self.session, matchday, self.currentMatchday, self.currentMatchday, self, self.parent, 980, 550, GREY_BACKGROUND, 0, 0, "nw")
            else:
                frame = None
            
            self.frames.append(frame)

    def addButtons(self):
        self.back5Button = ctk.CTkButton(self.buttonsFrame, text = "<<", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 90, hover_color = GREY_BACKGROUND, command = lambda: self.changeFrame(-5))
        self.back5Button.place(relx = 0.05, rely = 0.5, anchor = "center")

        self.back1Button = ctk.CTkButton(self.buttonsFrame, text = "<", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 90, hover_color = GREY_BACKGROUND, command = lambda: self.changeFrame(-1))
        self.back1Button.place(relx = 0.15, rely = 0.5, anchor = "center")

        self.currentMatchdayButton = ctk.CTkButton(self.buttonsFrame, text = "Current Matchday", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 580, hover_color = GREY_BACKGROUND, state = "disabled", command = self.go_currentMatchday)
        self.currentMatchdayButton.place(relx = 0.5, rely = 0.5, anchor = "center")

        self.forward1Button = ctk.CTkButton(self.buttonsFrame, text = ">", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 90, hover_color = GREY_BACKGROUND, command = lambda: self.changeFrame(1))
        self.forward1Button.place(relx = 0.85, rely = 0.5, anchor = "center")

        self.forward5Button = ctk.CTkButton(self.buttonsFrame, text = ">>", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 90, hover_color = GREY_BACKGROUND, command = lambda: self.changeFrame(5))
        self.forward5Button.place(relx = 0.95, rely = 0.5, anchor = "center")

    def changeFrame(self, direction):
        self.frames[self.activeFrame].place_forget()

        if self.activeFrame + direction > self.numMacthdays - 1:
            self.activeFrame = (direction - (self.numMacthdays - self.activeFrame))
        elif self.activeFrame + direction < 0:
            self.activeFrame = self.numMacthdays - (abs(direction) - self.activeFrame)
        else:
            self.activeFrame += direction

        if self.activeFrame == self.currentMatchday - 1:
            self.currentMatchdayButton.configure(state = "disabled")
        else:
            self.currentMatchdayButton.configure(state = "normal")

        if self.frames[self.activeFrame]:
            self.frames[self.activeFrame].placeFrame()
        else:
            matchday = Matches.get_matchday_for_league(self.session, self.league.id, self.activeFrame + 1)
            self.frames[self.activeFrame] = MatchdayFrame(self, self.session, matchday, self.activeFrame + 1, self.currentMatchday, self, self.parent, 980, 550, GREY_BACKGROUND, 0, 0, "nw")

    def go_currentMatchday(self):
        self.frames[self.activeFrame].place_forget()

        self.frames[self.currentMatchday - 1].placeFrame()
        self.activeFrame = self.currentMatchday - 1

        self.currentMatchdayButton.configure(state = "disabled")

class Graphs(ctk.CTkFrame):
    def __init__(self, parent, session, league):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.session = session
        self.league = league
        self.leagueTeams = LeagueTeams.get_teams_by_position(self.session, self.league.id)
        self.numTeams = len(self.leagueTeams)

        self.columns = (self.numTeams * 2) - 3
        self.canvasWidth = 945
        self.canvasHeight = 680
        
        self.graph = "positions"

        self.tableFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 200, height = 620, corner_radius = 15)
        self.tableFrame.place(relx = 0, rely = 0, anchor = "nw")
        self.tableFrame.pack_propagate(False)
    
        self.addTeams()

        canvas = ctk.CTkCanvas(self, width = 5, height = 750, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.2, rely = 0.48, anchor = "center")

        self.buttonsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 760, height = 60, corner_radius = 15)
        self.buttonsFrame.place(relx = 0.98, rely = 0.98, anchor = "se")

        self.addButtons()

        self.positionsCanvas = ctk.CTkCanvas(self, width = self.canvasWidth, height = self.canvasHeight, bg = TKINTER_BACKGROUND, bd = 0, highlightthickness = 0)
        self.positionsCanvas.place(relx = 0.98, rely = 0, anchor = "ne")

        self.pointsCanvas = ctk.CTkCanvas(self, width = self.canvasWidth, height = self.canvasHeight, bg = TKINTER_BACKGROUND, bd = 0, highlightthickness = 0)

        self.drawGrid(self.positionsCanvas, self.numTeams - 1, "positions")
        self.drawGrid(self.pointsCanvas, max(15, self.leagueTeams[0].points), "points")  

        for i, team in enumerate(self.leagueTeams):
            team = Teams.get_team_by_id(self.session, team.team_id)

            positions_result = TeamHistory.get_positions_by_team(self.session, team.id)
            if positions_result:
                positions = [pos[0] for pos in positions_result]  # Convert tuple to list
                self.createGraphs(positions, i, self.numTeams - 1, "positions", self.positionsCanvas)

            points_result = TeamHistory.get_points_by_team(self.session, team.id)
            if points_result:
                points = [poi[0] for poi in points_result]  # Convert tuple to list
                self.createGraphs(points, i, max(15, self.leagueTeams[0].points), "points", self.pointsCanvas)

    def addTeams(self):

        for i, team in enumerate(self.leagueTeams):
            teamData = Teams.get_team_by_id(self.session, team.team_id)

            frame = ctk.CTkFrame(self.tableFrame, fg_color = TKINTER_BACKGROUND, width = 200, height = 21)
            frame.pack(fill = "both", pady = 5, padx = 5)

            src = Image.open(io.BytesIO(teamData.logo))
            src.thumbnail((20, 20))
            logo = ctk.CTkImage(src, None, (src.width, src.height))

            imageLabel = ctk.CTkLabel(frame, image = logo, text = "", fg_color = TKINTER_BACKGROUND)
            imageLabel.place(relx = 0.95, rely = 0.5, anchor = "e")
            nameLabel = ctk.CTkLabel(frame, text = teamData.name, font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND)
            nameLabel.place(relx = 0.8, rely = 0.5, anchor = "e")
            
            frame.bind("<Enter>", lambda event, f = frame, i = imageLabel, n = nameLabel: self.onFrameHover(event, f, i, n))
            frame.bind("<Leave>", lambda event, f = frame, i = imageLabel, n = nameLabel: self.onFrameLeave(event, f, i, n))
            imageLabel.bind("<Enter>", lambda event, f = frame, i = imageLabel, n = nameLabel: self.onFrameHover(event, f, i, n))
            imageLabel.bind("<Leave>", lambda event, f = frame, i = imageLabel, n = nameLabel: self.onFrameLeave(event, f, i, n))
            nameLabel.bind("<Enter>", lambda event, f = frame, i = imageLabel, n = nameLabel: self.onFrameHover(event, f, i, n))
            nameLabel.bind("<Leave>", lambda event, f = frame, i = imageLabel, n = nameLabel: self.onFrameLeave(event, f, i, n))

            frame.bind("<Button-1>", lambda event, team_id = teamData.id, i = i, f = frame, im = imageLabel, n = nameLabel: self.selectTeam(team_id, i, f, im, n))
            imageLabel.bind("<Button-1>", lambda event, team_id = teamData.id, i = i, f = frame, im = imageLabel, n = nameLabel: self.selectTeam(team_id, i, f, im, n))
            nameLabel.bind("<Button-1>", lambda event, team_id = teamData.id, i = i, f = frame, im = imageLabel, n = nameLabel: self.selectTeam(team_id, i, f, im, n))
            
    def onFrameHover(self, event, frame, img, name):
        frame.configure(fg_color = GREY_BACKGROUND)
        img.configure(fg_color = GREY_BACKGROUND)
        name.configure(fg_color = GREY_BACKGROUND)

    def onFrameLeave(self, event, frame, img, name):
        frame.configure(fg_color = TKINTER_BACKGROUND)
        img.configure(fg_color = TKINTER_BACKGROUND)
        name.configure(fg_color = TKINTER_BACKGROUND)

    def createGraphs(self, positions, index, rows, graph, canvas, first = True, delete = False):

        canvas = self.positionsCanvas if graph == "positions" else self.pointsCanvas

        if delete:
            canvas.delete("non_image")
        elif not first and not delete:
            canvas.delete("line" + str(index))
            return

        # Calculate the size of each cell
        cellWidth = (self.canvasWidth - 50) / self.columns
        cellHeight = (self.canvasHeight - 40) / rows

        # Store the coordinates of each point
        points = []

        # Draw a point on each row
        for i, position in enumerate(positions):
            x = 20 + i * cellWidth  # Place the point on the grid line

            if graph == "positions":
                y = 20 + (int(position) - 1) * cellHeight  # Place the point on the grid line
            else:
                y = 20 + (rows - int(position)) * cellHeight

            # Add the coordinates of the point to the list
            points.append(x)
            points.append(y)

        if len(points) >= 4:
            # Draw a line connecting all points with a wider line
            if not delete and first:
                canvas.create_line(*points, fill = TABLE_COLOURS[index], width = 2, tags = "non_image")
            elif not first and delete:
                canvas.create_line(*points, fill = TABLE_COLOURS[index], width = 2, tags = "line" + str(index))
        else:
            if not delete and first:
                canvas.create_oval(points[0] - 2, points[1] - 2, points[0] + 2, points[1] + 2, fill=TABLE_COLOURS[index], tags="non_image")
            elif not first and delete:
                canvas.create_oval(points[0] - 2, points[1] - 2, points[0] + 2, points[1] + 2, fill=TABLE_COLOURS[index], tags="line" + str(index))

    def drawGrid(self, canvas, rows, graph):
        # Calculate the size of each cell
        cellWidth = (self.canvasWidth - 50) / self.columns  # Subtract 50 to add a space of 20 pixels on the left and 30 on the right
        cellHeight = (self.canvasHeight - 40) / rows  # Subtract 40 to add a space of 20 pixels on the top and bottom

        # Draw vertical lines
        for i in range(self.columns):
            x = i * cellWidth + 20  # Add 20 to move the grid 20 pixels to the right
            if i == 0:
                canvas.create_line(x, 20, x, self.canvasHeight - 20, fill = "white")  # Solid white line for the leftmost vertical line
            else:
                canvas.create_line(x, 20, x, self.canvasHeight - 20, fill = GREY_BACKGROUND, dash = (4, 2))  # Dashed line for other vertical lines

            # Add matchDays at the bottom of each column
            if i == 0 or (i + 1) % 5 == 0:
                canvas.create_text(x, self.canvasHeight - 12, text = str(i + 1), anchor = "n", fill = "white")  # Subtract 10 to move the text up 10 pixels at the bottom

        # Draw the last vertical line
        canvas.create_line(self.canvasWidth - 30, 20, self.canvasWidth - 30, self.canvasHeight - 20, fill = GREY_BACKGROUND, dash = (4, 2))  # Dashed line for the last vertical line

        # Add the last matchDay at the bottom
        canvas.create_text(self.canvasWidth - 30, self.canvasHeight - 12, text = str(self.columns + 1), anchor = "n", fill = "white")  # Subtract 30 to move the text 30 pixels to the left and subtract 10 to move it up 10 pixels at the bottom

        # Draw horizontal lines
        for i in range(rows):
            y = i * cellHeight + 20  # Add 20 to move the lines down 20 pixels
            if i == rows:
                canvas.create_line(20, y, self.canvasWidth - 30, y, fill = "white")  # Solid white line for the bottom horizontal line
            else:
                canvas.create_line(25, y, self.canvasWidth - 30, y, fill = GREY_BACKGROUND, dash = (4, 2))  # Dashed line for other horizontal lines

            # Add row number at the top of the row
            if graph == "positions":
                canvas.create_text(10, y - 8, text = str(i + 1), anchor = "n", fill = "white")  # Move the text 10 pixels to the left
            else:
                if i == 0 or (rows - i) % 5 == 0:
                    canvas.create_text(10, y - 8, text = str(rows - i), anchor = "n", fill = "white")

        # Draw the last horizontal line
        canvas.create_line(20, self.canvasHeight - 20, self.canvasWidth - 30, self.canvasHeight - 20, fill = "white")  # Solid white line for the bottom horizontal line

        # Add the last row number
        if graph == "positions":
            canvas.create_text(10, self.canvasHeight - 28, text = self.numTeams, anchor = "n", fill = "white")  # Move the text 10 pixels to the left and subtract 20 to move it up 20 pixels at the bottom
        else:
            canvas.create_text(10, self.canvasHeight - 28, text = "0", anchor = "n", fill = "white")

    def addButtons(self):
        self.positionsButton = ctk.CTkButton(self.buttonsFrame, text = "Positions", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 300, hover_color = GREY_BACKGROUND, state = "disabled", command = lambda: self.changeGraph("positions"))
        self.positionsButton.place(relx = 0.2, rely = 0.5, anchor = "center")

        self.pointsButton = ctk.CTkButton(self.buttonsFrame, text = "Points", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 300, hover_color = GREY_BACKGROUND, command = lambda: self.changeGraph("points"))
        self.pointsButton.place(relx = 0.6, rely = 0.5, anchor = "center")

        self.resetButton = ctk.CTkButton(self.buttonsFrame, text = "Reset", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 150, hover_color = GREY_BACKGROUND, state = "disabled", command = self.resetGraph)
        self.resetButton.place(relx = 0.9, rely = 0.5, anchor = "center")

    def changeGraph(self, graph):
        self.resetGraph()
        if graph == "points":
            self.graph = "points"
            self.positionsCanvas.place_forget()
            self.pointsCanvas.place(relx = 0.98, rely = 0, anchor = "ne")
            self.positionsButton.configure(state = "normal")
            self.pointsButton.configure(state = "disabled")

        else:
            self.graph = "positions"
            self.pointsCanvas.place_forget()
            self.positionsCanvas.place(relx = 0.98, rely = 0, anchor = "ne")
            self.positionsButton.configure(state = "disabled")
            self.pointsButton.configure(state = "normal")

    def resetGraph(self):
        if self.graph == "positions":
            self.positionsCanvas.delete("all")

            self.drawGrid(self.positionsCanvas, self.numTeams - 1, "positions")

            for i, team in enumerate(self.leagueTeams):
                team = Teams.get_team_by_id(self.session, team.team_id)

                positions_result = TeamHistory.get_positions_by_team(self.session, team.id)
                if positions_result:
                    positions = [pos[0] for pos in positions_result]  # Convert tuple to list
                    self.createGraphs(positions, i, self.numTeams - 1, "positions", self.positionsCanvas)

        else:
            self.pointsCanvas.delete("all")

            self.drawGrid(self.pointsCanvas, max(15, self.leagueTeams[0].points), "points")

            for i, team in enumerate(self.leagueTeams):
                team = Teams.get_team_by_id(self.session, team.team_id)

                points_result = TeamHistory.get_points_by_team(self.session, team.id)
                if points_result:
                    points = [poi[0] for poi in points_result]  # Convert tuple to list
                    self.createGraphs(points, i, max(15, self.leagueTeams[0].points), "points", self.pointsCanvas)

        self.resetButton.configure(state = "disabled")

        for i, widget in enumerate(self.tableFrame.winfo_children()):
            img = widget.winfo_children()[0]
            name = widget.winfo_children()[1]

            team = Teams.get_team_by_name(self.session, name.cget("text"))

            widget.unbind("<Button-1>")
            img.unbind("<Button-1>")
            name.unbind("<Button-1>")

            widget.bind("<Button-1>", lambda event, team_id = team.id, i = i, f = widget, im = img, n = name: self.selectTeam(team_id, i, f, im, n))
            img.bind("<Button-1>", lambda event, team_id = team.id, i = i, f = widget, im = img, n = name: self.selectTeam(team_id, i, f, im, n))
            name.bind("<Button-1>", lambda event, team_id = team.id, i = i, f = widget, im = img, n = name: self.selectTeam(team_id, i, f, im, n))

    def selectTeam(self, team_id, index, frame, img, name):
        if self.graph == "positions":
            positions_result = TeamHistory.get_positions_by_team(self.session, team_id)
            if positions_result:
                positions = [pos[0] for pos in positions_result]
                self.createGraphs(positions, index, self.numTeams - 1, "positions", self.positionsCanvas, False, True)
        else:
            points_result = TeamHistory.get_points_by_team(self.session, team_id)
            if points_result:
                points = [poi[0] for poi in points_result]
                self.createGraphs(points, index, max(15, self.leagueTeams[0].points), "points", self.pointsCanvas, False, True)

        self.resetButton.configure(state = "normal")

        frame.unbind("<Button-1>")
        img.unbind("<Button-1>")
        name.unbind("<Button-1>")
        frame.bind("<Button-1>", lambda event, team_id = team_id, i = index, f = frame, im = img, n = name: self.deselectTeam(team_id, i, f, im, n))
        img.bind("<Button-1>", lambda event, team_id = team_id, i = index, f = frame, im = img, n = name: self.deselectTeam(team_id, i, f, im, n))
        name.bind("<Button-1>", lambda event, team_id = team_id, i = index, f = frame, im = img, n = name: self.deselectTeam(team_id, i, f, im, n))

    def deselectTeam(self, team_id, index, frame, img, name):
        if self.graph == "positions":
            positions_result = TeamHistory.get_positions_by_team(self.session, team_id)
            if positions_result:
                positions = [pos[0] for pos in positions_result]
                self.createGraphs(positions, index, self.numTeams - 1, "positions", self.positionsCanvas, False, False)
        else:
            points_result = TeamHistory.get_points_by_team(self.session, team_id)
            if points_result:
                points = [poi[0] for poi in points_result]
                self.createGraphs(points, index, max(15, self.leagueTeams[0].points), "points", self.pointsCanvas, False, False)

        self.resetButton.configure(state = "disabled")

        frame.unbind("<Button-1>")
        img.unbind("<Button-1>")
        name.unbind("<Button-1>")
        frame.bind("<Button-1>", lambda event, team_id = team_id, i = index, f = frame, im = img, n = name: self.selectTeam(team_id, i, f, im, n))
        img.bind("<Button-1>", lambda event, team_id = team_id, i = index, f = frame, im = img, n = name: self.selectTeam(team_id, i, f, im, n))
        name.bind("<Button-1>", lambda event, team_id = team_id, i = index, f = frame, im = img, n = name: self.selectTeam(team_id, i, f, im, n))

class History(ctk.CTkScrollableFrame):
    def __init__(self, parent, session, league):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 965, height = 630, corner_radius = 0) 

        self.parent = parent
        self.session = session
        self.league = league