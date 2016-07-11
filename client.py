#!/usr/bin/python 

# requirements
import json
import requests
import ConfigParser
from Tkinter import *
from termcolor import colored

# photo
photo = None

# cache
vehicles = []
users = []
gss = []

# quit
def quit():  
    sys.exit()


# fetch data 
def load_data():

    # debug print
    print colored("load_data> ", "blue", attrs=["bold"]) + "fetching data..."
   
    # clear the old lists
    global vehicles
    global users
    global gss
    vehicles = []
    users = []
    gss = []

    # define urls and headers
    headers = {'Accept' : 'application/json'}
    users_url = "http://%s:%s/users" % (settings["host"], settings["port"])
    vehicles_url = "http://%s:%s/vehicles" % (settings["host"], settings["port"])
    gss_url = "http://%s:%s/groundstations" % (settings["host"], settings["port"])
    evses_url = "http://%s:%s/bs/evses" % (settings["host"], settings["port"])
    check_otmres_url = "http://%s:%s/reservations" % (settings["host"], settings["port"])

    # clear the old content of the listboxes
    listbox_vehicles.delete(0, END)
    listbox_users.delete(0, END)
    listbox_gss.delete(0, END)
    
    # get vehicles
    reply = requests.get(vehicles_url, headers=headers)
    json_reply = json.loads(reply.text)
    for vehicle in json_reply["results"]:
        vehicles.append(vehicle["vehicle_id"])
        listbox_vehicles.insert(END, vehicle["vehicle_id"])
        
    # get users
    reply = requests.get(users_url, headers=headers)
    json_reply = json.loads(reply.text)
    for user in json_reply["results"]:
        users.append(user["user_uid"])
        listbox_users.insert(END, user["user_uid"])
        
    # retrieve the recharge type
    rt = recharge_type.get()
    if rt == "0":

        # get evses
        reply = requests.get(evses_url, headers=headers)
        json_reply = json.loads(reply.text)
        for evse in json_reply["results"]:
            gss.append(evse["id"])
            listbox_gss.insert(END, evse["id"])

        # set the label to "EVSEs:"
        label_gss.config(text = "EVSEs:")

    else:
    
        # get gss
        reply = requests.get(gss_url, headers=headers)
        json_reply = json.loads(reply.text)
        for gs in json_reply["results"]:
            gss.append(gs["gs_id"])
            listbox_gss.insert(END, gs["gs_id"])
    
        # set the label to "GSs:"
        label_gss.config(text = "Ground Stations:")


def check_reservation():

    # define urls and headers
    headers = {'Accept' : 'application/json', 'Content-type' : 'application/json'}
    check_otmres_url = "http://%s:%s/reservations/status" % (settings["host"], settings["port"])

    # retrieve the recharge type
    rt = recharge_type.get()
    if rt == "0":

        print colored("check_reservation> ", "blue", attrs=["bold"]) + "Checking traditional reservation...",

        # made the request to check reservation
        request_content = json.dumps({
            "gs_id" : gss[listbox_gss.curselection()[0]],
            "vehicle_id" : vehicles[listbox_vehicles.curselection()[0]],
            "user_id" : users[listbox_users.curselection()[0]],
            "res_type" : "TRA"
        })
        try:
            reply = requests.get(check_otmres_url, headers=headers, data=request_content)
            json_reply = json.loads(reply.text)
            print colored("Done!", "green", attrs=["bold"])
        except Exception as e:
            print colored("FAILED!", "red", attrs=["bold"])
                
    else:
        
        print colored("check_reservation> ", "blue", attrs=["bold"]) + "Checking OnTheMove reservation...",
               
        # made the request to check reservation
        request_content = json.dumps({
            "gs_id" : gss[listbox_gss.curselection()[0]],
            "vehicle_id" : vehicles[listbox_vehicles.curselection()[0]],
            "user_id" : users[listbox_users.curselection()[0]],
            "res_type" : "OTM"
        })
        try:
            reply = requests.get(check_otmres_url, headers=headers, data=request_content)
            json_reply = json.loads(reply.text)        
            print colored("Done!", "green", attrs=["bold"])
        except Exception as e:
            print colored("FAILED!", "red", attrs=["bold"])

    global photo
    if json_reply.has_key("error"):
        photo = PhotoImage(file = "images/Boton-mal-300px.png")
        status_label.configure(image = photo, state = NORMAL)
    elif json_reply.has_key("OK"):
        photo = PhotoImage(file = "images/Boton-correcto-300px.png")
        status_label.configure(image = photo, state = NORMAL)


# read configuration
print colored("main> ", "blue", attrs=["bold"]) + "reading configuration"
settings = {}
settingsParser = ConfigParser.ConfigParser()
settingsParser.readfp(open("otmclient.conf"))
settings["host"] = settingsParser.get("service", "host")
settings["port"] = settingsParser.getint("service", "port")

# main window
root = Tk()
root.title("OTM Reservation Inspector")

# recharge type selection
recharge_type = StringVar()
recharge_type.set("1")
radio_tra = Radiobutton(root, text="Traditional", variable=recharge_type, value="0", command = load_data)
radio_tra.grid(row = 0, column = 0)
radio_otm = Radiobutton(root, text="On The Move", variable=recharge_type, value="1", command = load_data)
radio_otm.grid(row = 0, column = 1)

# ground stations section
frame_gss = Frame(root)
label_gss = Label(root, text="Ground Stations:")
label_gss.grid(row = 1, columnspan = 3)
scrollbar_gss = Scrollbar(frame_gss)
scrollbar_gss.pack(side = RIGHT, fill = Y)
listbox_gss = Listbox(frame_gss, exportselection = False, width = 50, yscrollcommand = scrollbar_gss.set)
listbox_gss.pack()
scrollbar_gss.config(command = listbox_gss.yview)
frame_gss.grid(row = 2, columnspan=3)

# users section
frame_users = Frame(root)
label_users = Label(root, text="Users:")
label_users.grid(row = 3, columnspan = 3)
scrollbar_users = Scrollbar(frame_users)
scrollbar_users.pack(side = RIGHT, fill = Y)
listbox_users = Listbox(frame_users, exportselection = False, width = 50, yscrollcommand = scrollbar_users.set)
listbox_users.pack()
frame_users.grid(row = 4, columnspan = 3)

# vehicles section
frame_vehicles = Frame(root)
label_vehicles = Label(root, text="Vehicles:")
label_vehicles.grid(row = 5, columnspan = 3)
scrollbar_vehicles = Scrollbar(frame_vehicles)
scrollbar_vehicles.pack(side = RIGHT, fill = Y)
listbox_vehicles = Listbox(frame_vehicles, exportselection = False, width = 50, yscrollcommand = scrollbar_vehicles.set)
listbox_vehicles.pack()
frame_vehicles.grid(row = 6, columnspan = 3)

# check button
check_image = PhotoImage(file = "images/system-search-32px.png")
button_check = Button(root, text="Check", command=check_reservation, compound = "left", image = check_image)
button_check.grid(row = 7, column = 0, sticky = "WE")

# reload button
reload_image = PhotoImage(file = "images/rodentia-icons_view-refresh-32px.png")
button_reload = Button(root, text="Refresh", command=load_data, compound = "left", image = reload_image)
button_reload.grid(row = 7, column = 1, sticky = "WE")

# quit button
quit_image = PhotoImage(file = "images/system-log-out-32px.png")
button_quit = Button(root, command = quit, image = quit_image, text = "Quit", compound = "left")
button_quit.grid(row = 7, column = 2, sticky = "WE")

# status label
photo = PhotoImage(file = "images/Boton-correcto-300px.png")
status_label = Label(root, image = photo, state = DISABLED)
status_label.grid(row = 8, columnspan = 3)

# fetch data
load_data()

# start the main loop
try:
    root.mainloop()
except KeyboardInterrupt:
    root.destroy()
