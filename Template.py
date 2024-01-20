import random
import sys
import tkinter
import tkinter.messagebox
from tkintermapview import TkinterMapView
from pyswip import Prolog
import pandas as pd


class App(tkinter.Tk):
    APP_NAME = "map_view_demo.py"
    WIDTH = 800
    HEIGHT = 750  # This is now the initial size, not fixed.

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)

        self.title(self.APP_NAME)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        # Configure the grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Text area and submit button combined row
        self.grid_rowconfigure(1, weight=4)  # Map row

        # Upper part: Text Area and Submit Button
        self.text_area = tkinter.Text(self, height=5)  # Reduced height for text area
        self.text_area.grid(row=0, column=0, pady=(10, 0), padx=10, sticky="nsew")

        self.submit_button = tkinter.Button(self, text="Submit", command=self.process_text)
        # Placed within the same cell as text area
        self.submit_button.grid(row=0, column=0, pady=(0, 10), padx=10, sticky="se")

        # Lower part: Map Widget
        self.map_widget = TkinterMapView(self)
        self.map_widget.grid(row=1, column=0, sticky="nsew")

        self.marker_list = []  # Keeping track of markers
        self.marker_path = None

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)

        self.title(self.APP_NAME)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        # Configure the grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Text area can expand/contract.
        self.grid_rowconfigure(1, weight=0)  # Submit button row; doesn't need to expand.
        self.grid_rowconfigure(2, weight=3)  # Map gets the most space.

        # Upper part: Text Area and Submit Button
        self.text_area = tkinter.Text(self)
        self.text_area.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")

        self.submit_button = tkinter.Button(self, text="Submit", command=self.process_text)
        self.submit_button.grid(row=1, column=0, pady=10, sticky="ew")

        # Lower part: Map Widget
        self.map_widget = TkinterMapView(self)
        self.map_widget.grid(row=2, column=0, sticky="nsew")

        self.marker_list = []  # Keeping track of markers

    def check_connections(self, results, dic):

        copy_results = results.copy()
        locations = set()

        prolog.retractall("directly_connected(_,_)")
        prolog.retractall("connected(_,_)")

        adj_matrix = pd.read_csv('Adjacency_matrix.csv')

        for index, row in adj_matrix.iterrows():
            if row["Destination"] in copy_results:
                for column in adj_matrix.columns:
                    if column != "Destination":
                        if adj_matrix.at[index, column] == 1 and column.lower() in results:
                            prolog.assertz(f"directly_connected({row['Destination'].lower()},{column.lower()})")
                copy_results.remove(row["Destination"])

        prolog.assertz("connected(X, Y) :- directly_connected(X, Y)")
        prolog.assertz("connected(Y, X) :- directly_connected(X, Y)")
        prolog.assertz("connected(X, Y) :- directly_connected(X, Z), connected(Z, Y)")
        prolog.assertz("connected(X, Y) :- directly_connected(X, Z), directly_connected(Z, W), directly_connected(W, Y)")

        for result in results:
            query = f"connected({result.lower()}, X)"
            connected = list(prolog.query(query))
            for destination in connected:
                locations.add(destination["X"])

        max_features = len(dic)
        org_locations = set()
        if len(locations) == 0:

            while True:
                for location in results:
                    count = 0
                    for key, value in dic.items():
                        if location in dic[key]:
                            count += 1
                        if count == max_features:
                            org_locations.add(location)
                if len(org_locations) >= 5:
                    break
                else:
                    max_features -= 1
                    org_locations = set()

        elif len(locations) > 0:

            while True:
                for location in locations:
                    count = 0
                    for key, value in dic.items():
                        if location in dic[key]:
                            count += 1
                        if count == max_features:
                            org_locations.add(location)
                if len(org_locations) >= 5:
                    break
                else:
                    max_features -= 1
                    org_locations = set()

        if len(org_locations) < 5:
            output = list(org_locations)
        else:
            output = random.sample(list(org_locations), 5)
        return output

    def process_text(self):
        """Extract locations from the text area and mark them on the map."""
        text = self.text_area.get("1.0", "end-1c")  # Get text from text area
        results, dic = self.extract_locations(text)  # Extract locations (you may use a more complex method here)
        locations = self.check_connections(results, dic)
        print(locations)
        self.mark_locations(locations)

    def mark_locations(self, locations):
        """Mark extracted locations on the map."""
        for address in locations:
            marker = self.map_widget.set_address(address, marker=True)
            if marker:
                self.marker_list.append(marker)
        self.connect_marker()
        self.map_widget.set_zoom(1)  # Adjust as necessary, 1 is usually the most zoomed out

    def connect_marker(self):
        print(self.marker_list)
        position_list = []

        for marker in self.marker_list:
            position_list.append(marker.position)

        if hasattr(self, 'marker_path') and self.marker_path is not None:
            self.map_widget.delete(self.marker_path)

        if len(position_list) > 0:
            self.marker_path = self.map_widget.set_path(position_list)

    def extract_locations(self, text):
        words = text.split()
        keyword = {}
        locations = set()
        for word in words:
            if word in DESTINATION:
                keyword["destination"].append(word)
            elif word in COUNTRY:
                keyword["country"].append(word)
            elif word in REGION:
                keyword["region"].append(word)
            elif word in CLIMATE:
                keyword["climate"].append(word)
            elif word in BUDGET:
                keyword["budget"].append(word)
            elif word in ACTIVITY:
                keyword["activity"].append(word)
            elif word in DEMOGRAPHICS:
                keyword["demographics"].append(word)
            elif word in DURATION:
                keyword["duration"].append(word)
            elif word in CUISINE:
                keyword["cuisine"].append(word)
            elif word in HISTORY:
                keyword["history"].append(word)
            elif word in NATURAL_WONDER:
                keyword["natural_wonder"].append(word)
            elif word in ACCOMMODATION:
                keyword["accommodation"].append(word)
            elif word in LANGUAGE:
                keyword["language"].append(word)

        dic = {}
        for key, value in keyword.items():
            for i in value:
                query = f"{key}(Destination, {i.lower()})"
                results = list(prolog.query(query))
                temp = set()
                for result in results:
                    locations.add(result["Destination"])
                    temp.add(result["Destination"])
                dic[key] = temp

        return locations, dic

    def start(self):
        self.mainloop()


# ...... create prolog

prolog = Prolog()

# ...... delete history

prolog.retractall("destinations(_,_)")
prolog.retractall("country(_,_)")
prolog.retractall("region(_,_)")
prolog.retractall("climate(_,_)")
prolog.retractall("budget(_,_)")
prolog.retractall("activity(_,_)")
prolog.retractall("demographics(_,_)")
prolog.retractall("duration(_,_)")
prolog.retractall("cuisine(_,_)")
prolog.retractall("history(_,_)")
prolog.retractall("natural_wonder(_,_)")
prolog.retractall("accommodation(_,_)")
prolog.retractall("language(_,_)")

# ....... create knowledge base (flat bag)

dataframe = pd.read_csv('Destinations.csv')


for index, row in dataframe.iterrows():
    prolog.assertz(f"destination('{row['Destination'].replace(" ", "-").replace(".", "")}')")
    prolog.assertz(f"country('{row['Destination'].replace(" ", "-").replace(".", "")}', '{row['Country'].replace(" ", "-").replace(".", "").lower()}')")
    prolog.assertz(f"region('{row['Destination'].replace(" ", "-").replace(".", "")}', '{row['Region'].replace(" ", "-").replace(".", "").lower()}')")
    prolog.assertz(f"climate('{row['Destination'].replace(" ", "-").replace(".", "")}', '{row['Climate'].replace(" ", "-").replace(".", "").lower()}')")
    prolog.assertz(f"budget('{row['Destination'].replace(" ", "-").replace(".", "")}', '{row['Budget'].replace(" ", "-").replace(".", "").lower()}')")
    prolog.assertz(f"activity('{row['Destination'].replace(" ", "-").replace(".", "")}', '{row['Activity'].replace(" ", "-").replace(".", "").lower()}')")
    prolog.assertz(f"demographics('{row['Destination'].replace(" ", "-").replace(".", "")}', '{row['Demographics'].replace(" ", "-").replace(".", "").lower()}')")
    prolog.assertz(f"duration('{row['Destination'].replace(" ", "-").replace(".", "")}', '{row['Duration'].replace(" ", "-").replace(".", "").lower()}')")
    prolog.assertz(f"cuisine('{row['Destination'].replace(" ", "-").replace(".", "")}', '{row['Cuisine'].replace(" ", "-").replace(".", "").lower()}')")
    prolog.assertz(f"history('{row['Destination'].replace(" ", "-").replace(".", "")}', '{row['History'].replace(" ", "-").replace(".", "").lower()}')")
    prolog.assertz(f"natural_wonder('{row['Destination'].replace(" ", "-").replace(".", "")}', '{row['Natural_Wonder'].replace(" ", "-").replace(".", "").lower()}')")
    prolog.assertz(f"accommodation('{row['Destination'].replace(" ", "-").replace(".", "")}', '{row['Accommodation'].replace(" ", "-").replace(".", "").lower()}')")
    prolog.assertz(f"language('{row['Destination'].replace(" ", "-").replace(".", "")}', '{row['Language'].replace(" ", "-").replace(".", "").lower()}')")

# ...... extract unique features

DESTINATION = set()
COUNTRY = set()
REGION = set()
CLIMATE = set()
BUDGET = set()
ACTIVITY = set()
DEMOGRAPHICS = set()
DURATION = set()
CUISINE = set()
HISTORY = set()
NATURAL_WONDER = set()
ACCOMMODATION = set()
LANGUAGE = set()

for index, row in dataframe.iterrows():
    DESTINATION.add(row['Destination'].lower())
    COUNTRY.add(row['Country'].lower())
    REGION.add(row['Region'].lower())
    CLIMATE.add(row['Climate'].lower())
    BUDGET.add(row['Budget'].lower())
    ACTIVITY.add(row['Activity'].lower())
    DEMOGRAPHICS.add(row['Demographics'].lower())
    DURATION.add(row['Duration'].lower())
    CUISINE.add(row['Cuisine'].lower())
    HISTORY.add(row['History'].lower())
    NATURAL_WONDER.add(row['Natural_Wonder'].lower())
    ACCOMMODATION.add(row['Accommodation'].lower())
    LANGUAGE.add(row['Language'].lower())

if __name__ == "__main__":
    app = App()
    app.start()

