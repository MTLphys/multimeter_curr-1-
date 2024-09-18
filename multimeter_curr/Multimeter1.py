
#multimeter controll library
import pyvisa as visa
#QT libraries
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtCore import QTimer
from PyQt5 import QtCore
import pyqtgraph as pg
#standard libraries
import sys
import threading
import time
import csv
#Matthew's Libraries
import GuiWrapper
#Library to query file name
from text_entry1 import TextBox

class MultimeterController(QWidget):
    # Add a signal for plot update
    plot_update_signal = QtCore.pyqtSignal(float, float,float)

    def __init__(self,plot_widget,multimeter_addresses,filename):
        super().__init__()
        #prepare multimeters
        self.multimeter_addresses = multimeter_addresses
        self.multimeters = [None, None]
        self.multimeters[0] = visa.ResourceManager().open_resource(self.multimeter_addresses[0])
        self.multimeters[1] = visa.ResourceManager().open_resource(self.multimeter_addresses[1])
        #location of data file
        self.filename  = filename
        #variable decarations/initialzations
        self.measurement_thread = None
        self.plot_widget = plot_widget
        self.position = None
        #flags
        self.done = False
        self.init_dmms = False
        self.measurements_done = False
        # Connect the signal to the slot for updating the plot
        self.plot_update_signal.connect(self.plot_widget.update_plot)
        #time for real time plot 
        self.start_time = time.time()  

    def start_measurements(self,position,mps,done):
        #flag to check if on last measurment
        self.done = done
        #begin measurement thread
        self.measurement_thread = threading.Thread(target=self.take_measurements,args=[position,mps])
        self.measurement_thread.start()

    def export_to_csv(self):
        position = self.plot_widget.position
        current  = self.plot_widget.current
        # Open the file for writing
        with open(self.filename, 'w', newline='') as csvfile:
            # Create a CSV writer object
            csvwriter = csv.writer(csvfile)
            
            # Write the header row
            csvwriter.writerow(['Position (mm)', 'Current (A)'])
            
            # Write the data rows
            for pos, cur in zip(position, current):
                csvwriter.writerow([pos, cur])

    def save_data(self):
        print("Saving Data...")
        self.export_to_csv()

    def normalize_measurement(self, measurement, reference):
        if reference == 0:
            #avoid division by zero
            return 0 
        return measurement / reference

    def take_measurements(self,position,mps):
        print("Measurements per Step: " + str(mps))
        print("Current Position: " + str(position))
        try:
            #take the number of current measurements specified my mps
            i = 0
            while i < mps:
                current = self.read_current()
                norm_current = self.normalize_measurement(current[0],current[1])
                if current is not None:
                    # Update plot with current
                    curr_time = time.time()  
                    self.plot_update_signal.emit( (curr_time - self.start_time),position,norm_current)
                i += 1
            #get ready for next measurement
            self.measurements_done = True
   
        except Exception as e:
            print("Error during current reading:", e)
        
    def read_current(self):
        #Set measurement function to DC current at  eggining of measurement
        if not self.init_dmms:
            self.multimeters[0].write('CONF:CURR:DC')
            self.multimeters[1].write('CONF:CURR:DC')
            self.init_dmms = True
        #read current from dmms
        curr1 = float(self.multimeters[0].query('READ?'))
        curr2 = float(self.multimeters[1].query('READ?'))
        return (curr1,curr2)

    def stop_measurement(self):
        #close measurment thread
        if self.measurement_thread and self.measurement_thread.is_alive():
            self.measurement_thread.join()
        #save data and terminate program when measurments are finished
        if self.done:
            self.save_data()
            self.closeEvent()
   
    def closeEvent(self):
        #close multimeter resources
        self.multimeters[0].close()
        self.multimeters[1].close()

class RealTimePlot(QWidget):
    def __init__(self):
        super().__init__()
        #initialize plot window
        self.setWindowTitle('Z-Scan Current Measurement')
        layout = QVBoxLayout()
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)

        # Initialize plot data for current measurments
        self.position = []
        self.current = []
        self.time_data = []
        #Create plot
        self.plot = self.plot_widget.plot(pen='r')  # 'r' for red
        #Label x-axis
        self.plot_widget.getAxis('bottom').setLabel("position (mm)")

    def update_plot(self, time, pos, curr):
        #push data to arrays 
        self.position.append(pos)
        self.current.append(curr)
        self.time_data.append(time)

        # Display last 30 seconds
        self.plot.setData(self.position, self.current)
        self.plot_widget.setXRange(min(self.position), max(self.position)+1)

        #extract magnitude and scale (scale * 10^magnitude)
        magnitude = str(curr).split('e')[1] if 'e' in str(curr) else '0'
        scale = str(curr).split('e')[0] if 'e' in str(curr) else '0'
        
        # Set y-axis range/labels
        self.plot_widget.setYRange(min(self.current)-.01, max(self.current)+.01)
        y_lab = "Current (A x 10^" + magnitude + ')'
        self.plot_widget.getAxis('left').setLabel(y_lab)

        # print("Current (A): "   + str(curr))
        # print("Position (mm): " + str(pos))

def find_multimeter_resources():
    #open pyvisa resource manager
    rm = visa.ResourceManager()
    try:
        #poll available multimeters
        available_resources = rm.list_resources()
        print("ResourceManager created successfully.")
        print(available_resources)
    except Exception as e:
        print("An error occurred:", e)
    #confirm we have 2 multimeter resources, if not, terminate the program
    if available_resources and len(available_resources) == 3 :
        return available_resources
    else:
        print("Inadequate multimeter resources.")
        return None

def init_multimeters(multimeters):
    # Prompt for filename
    text_box = TextBox(1)
    text_box.show()
    # Process events to show the text box immediately
    QApplication.processEvents() 

    #Wait for the user to enter the filename
    while text_box.isVisible():
        QApplication.processEvents()

    #Get the filename from text_entry
    filename = text_box.filename
    if not filename:
        return None

    #Initialize the plot window
    plot_window = RealTimePlot()
    plot_window.show()

    # Initialize the multimeter controller with the obtained filename
    controller = MultimeterController(plot_window, multimeters, filename)
    return controller

if __name__ == '__main__':

    #initializae QT
    app = QApplication(sys.argv)
    #get multimter addresses
    multimeters = find_multimeter_resources()
    if multimeters is None:
        sys.exit()
    #initialize multimeter controller
    controller = init_multimeters(multimeters)

    if controller == None:
        sys.exit()
    #display stage controller
    GuiWrapper.runGUIWrap(controller)
    #begin progam
    controller.show()

    sys.exit(app.exec_())