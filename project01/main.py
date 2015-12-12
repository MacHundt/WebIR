# coding: utf-8
"""The main file of the project."""

import tkinter
import webbrowser
import pickle

from utils.writing_style_analyzer import WritingStyleProcessor, WritingStyleLearner

__author__ = 'wikipedia_project_group'


class MainFrame(tkinter.Frame):
    gmaps_url = "https://www.google.de/maps/place/"
    result_country = ""
    result_confidence = 0

    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master)
        self.pack(side="top",
                  fill="both",
                  expand=True)

        self.analyze = None
        self.text_box = None
        self.processor = pickle.load(open("data/trained_processor", 'rb'))

        self.create_widgets()

    def create_widgets(self):
        self.create_text_box()
        self.analyse_button()

    def analyse_button(self):
        self.analyze = tkinter.Button(self)
        self.analyze["text"] = "Analyze text"
        self.analyze["command"] = self.analyse_func
        self.analyze.pack(side="bottom")

    def create_text_box(self):
        self.text_box = tkinter.Text()
        self.text_box.pack(side="top",
                           fill="both",
                           expand="True")

    def analyse_func(self):

        """
        variables to change:
        result_land
        result_confidence

        self.result_land, self.result_confidence = lukas_magic(input_text)

        just copy the above code under the input_text variable
        """
        try:
            input_text = self.text_box.get(1.0, tkinter.END)
            probabilities, self.result_country = self.processor.predict_text(input_text)
            self.result_confidence = 1 - probabilities.get(self.result_country)[2]

            self.open_results()
        except ZeroDivisionError as e:
            print(e)

    def open_results(self):
        results_frame = tkinter.Toplevel(self)
        label_top = tkinter.Label(results_frame, text="Results")
        label_top.pack(side="top")

        label_land = tkinter.Label(results_frame, text="Land: " + str(self.result_country))
        label_land.pack()

        label_confidence = tkinter.Label(results_frame, text="Confidence: %.2f" % (self.result_confidence * 100) + '%')
        label_confidence.pack()

        results_frame.show_map = tkinter.Button(results_frame)
        results_frame.show_map["text"] = "Show on Gmaps"
        results_frame.show_map["command"] = self.show_on_gmaps
        results_frame.show_map.pack(side="bottom")

    def show_on_gmaps(self):
        webbrowser.open_new_tab(self.gmaps_url + self.result_country)


def main():
    root = tkinter.Tk()
    root.title("Writing Style Predictor")
    app = MainFrame(root)
    app.mainloop()

if __name__ == '__main__':
    main()
