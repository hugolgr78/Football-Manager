import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class DragDropApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Drag and Drop with Multiple Zones")
        self.geometry("700x400")

        self.box_size = (100, 100)

        # Target positions
        self.green_target_pos = (500, 50)
        self.red_target_pos = (500, 250)

        # State: which zone is occupied and by whom (None, "A", or "B")
        self.zone_occupancy = {
            "green": None,
            "red": None
        }

        # Create target frames
        # Green target (not placed initially)
        self.green_target = ctk.CTkFrame(self, width=self.box_size[0], height=self.box_size[1],
                                        fg_color="transparent", border_width=2, border_color="green")

        # Red target (not placed initially)
        self.red_target = ctk.CTkFrame(self, width=self.box_size[0], height=self.box_size[1],
                                    fg_color="transparent", border_width=2, border_color="red")


        # Draggable A (blue)
        self.draggable_A = self.create_draggable("skyblue", [50, 50], "A")

        # Draggable B (orange)
        self.draggable_B = self.create_draggable("orange", [200, 50], "B")

    def create_draggable(self, color, origin, tag):
        frame = ctk.CTkFrame(self, width=self.box_size[0], height=self.box_size[1], fg_color=color)
        frame.place(x=origin[0], y=origin[1])
        frame.origin = origin
        frame.current_zone = None
        frame.tag = tag
        frame.drag_start_x = 0
        frame.drag_start_y = 0

        frame.bind("<Button-1>", self.start_drag)
        frame.bind("<B1-Motion>", self.do_drag)
        frame.bind("<ButtonRelease-1>", self.stop_drag)
        return frame

    def start_drag(self, event):
        widget = event.widget.master
        widget.drag_start_x = event.x
        widget.drag_start_y = event.y

        if self.zone_occupancy["green"] in [None, widget.tag]:
            self.green_target.place(x=self.green_target_pos[0], y=self.green_target_pos[1])
        if self.zone_occupancy["red"] in [None, widget.tag]:
            self.red_target.place(x=self.red_target_pos[0], y=self.red_target_pos[1])

    def do_drag(self, event):
        widget = event.widget.master
        new_x = widget.winfo_x() + event.x - widget.drag_start_x
        new_y = widget.winfo_y() + event.y - widget.drag_start_y
        widget.place(x=new_x, y=new_y)

    def check_overlap(self, widget, target_x, target_y):
        drag_x = widget.winfo_x()
        drag_y = widget.winfo_y()
        drag_w = widget.winfo_width()
        drag_h = widget.winfo_height()

        center_x = drag_x + drag_w // 2
        center_y = drag_y + drag_h // 2

        return (target_x <= center_x <= target_x + drag_w) and (target_y <= center_y <= target_y + drag_h)

    def stop_drag(self, event):
        widget = event.widget.master

        dropped = False

        self.green_target.place_forget()
        self.red_target.place_forget()

        # Try green zone
        if self.check_overlap(widget, self.green_target.winfo_x(), self.green_target.winfo_y()) and self.zone_occupancy["green"] in [None, widget.tag]:
            widget.place(x=self.green_target_pos[0], y=self.green_target_pos[1])
            widget.origin = list(self.green_target_pos)
            if widget.current_zone:
                self.zone_occupancy[widget.current_zone] = None
            self.zone_occupancy["green"] = widget.tag
            widget.current_zone = "green"
            dropped = True

        # Try red zone
        elif self.check_overlap(widget, self.red_target.winfo_x(), self.red_target.winfo_y()) and self.zone_occupancy["red"] in [None, widget.tag]:
            widget.place(x=self.red_target_pos[0], y=self.red_target_pos[1])
            widget.origin = list(self.red_target_pos)
            if widget.current_zone:
                self.zone_occupancy[widget.current_zone] = None
            self.zone_occupancy["red"] = widget.tag
            widget.current_zone = "red"
            dropped = True

        # If no valid drop, go back to origin
        if not dropped:
            widget.place(x=widget.origin[0], y=widget.origin[1])

        print(f"[{widget.tag}] is in zone: {widget.current_zone}")
        print(f"Zone Occupancy: {self.zone_occupancy}")


if __name__ == "__main__":
    app = DragDropApp()
    app.mainloop()
