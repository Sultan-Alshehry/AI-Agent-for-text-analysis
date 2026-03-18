import tkinter as t



def select_file():
    #This funktion creates and opens new screen that displays all the files that can be analyzid
    window.withdraw()
    global window2
    
    window2 = t.Toplevel()
    window2.geometry("400x400")
    window2.title("select document screen")
    window2.config(background="blue")
    
    label2 = t.Label(window2, text="select document to analyse")
    button2 = t.Button(window2, text="sports.pdf")
    button3 = t.Button(window2, text="data.txt")
    
    button2.config(command=sport_analysis)
    
    label2.pack()
    button2.pack()
    button3.pack()
    
def sport_analysis():
    #this funktion creates and opens screen that show result of analysis for sports file
    window2.withdraw()
    global Sport_screen
    
    Sport_screen = t.Toplevel()
    Sport_screen.geometry("400x400")
    Sport_screen.title("Sport analysis screen")
    Sport_screen.config(background="blue")
    
    back_button = t.Button(Sport_screen, text="Back")
    back_button.config(command=back)
    back_button.pack(anchor="nw")
    
    analysis_label = t.Label(Sport_screen, text=f"keyWord    relevance\n\n"
    f"ice hokey      8%\n"
    f"floor ball      5%\n"
    f"skiing              4,5%\n"
    f"bouldering    3%\n"
    f"dancing        2%\n"
    f"football          1,5%\n"
    f"futsal            1%"
    )
    analysis_label.pack()
    
def back():
    window.deiconify()
    Sport_screen.withdraw()

window = t.Tk() #this creates apps main screen
window.geometry("400x400") #defines main screens size
window.title("AITY program for text analysis") #changes the title of the main screen
window.config(background="blue") #change background color of the window

#icon = t.PhotoImage(file="Aity2.png") # load image
#window.iconphoto(True, icon) #change the logo

label = t.Label(window,                             #creating new label and attaching it to main screen
                text="welcome to AITY application", #putting text inside label
                font = ("arial", 12, "bold"),       #chaning font to ariel, and size to 12 and text to bold
                fg="green", bg="pink",              #changing foreground to green and background to pink
                relief=t.SUNKEN,                    #changing label to look like it is sunken inside main screen
                bd=10,                              #defining size of the edged of the screen
                )
label.pack() #packing the new label so it is shown inside the window

button = t.Button(window, text="Start new analysis") #creating button and attaching it to main screen
button.config(command=select_file) #defines the function that is called when the button is pressed
button.place(relx=0.6, rely=0.5, anchor="center") #determine the position of the button in the middle of the main screen

button4 = t.Button(window, text="View previous results") #creating button and attaching it to main screen
#button4.config(command=select_file) #defines the function that is called when the button is pressed
button4.place(relx=0.3, rely=0.5, anchor="center") #determine the position of the button in the middle of the main screen

window.mainloop() 