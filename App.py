from customtkinter import *
import sqlite3
import threading
import webbrowser
from component import scrapper_loop, cookie_save
from datetime import datetime



# target_date = datetime(3050, 12, 12)
# current_date = datetime.now()
url_db = 'https://www.facebook.com'
message_db = "Lorem ipusm is a"

con = sqlite3.connect('database.db')
cur = con.cursor()
cur.execute('''
            CREATE TABLE IF NOT EXISTS Postdata (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                url CHAR(20000),
                Message CHAR(500)
            )   
            ''')
data_check = cur.execute('''SELECT url FROM Postdata WHERE ID=1''').fetchone()
print(data_check)

if data_check == None:
    cur.execute(f'''
                    INSERT INTO Postdata(
                        url,
                        Message
                        )
                    VALUES(
                        '{url_db}',
                        '{message_db}'
                                               
                    )
                    ''')
# TK part
window = CTk()
set_default_color_theme("green")
set_appearance_mode("light")
window.title("FB Automate Posting")
window.geometry("620x600")
window.wm_iconbitmap()

# Create a Frame + Content Frame with scrollbar
frame = CTkFrame(window)
frame.pack(fill=BOTH, expand=True)
canvas = CTkCanvas(frame)
canvas.pack(side=LEFT, fill=BOTH, expand=True)
canvas.bind_all("<MouseWheel>", lambda event: on_mousewheel(event))  # Labda have to use when function is below
scrollbar = CTkScrollbar(frame, command=canvas.yview)
scrollbar.pack(side=RIGHT, fill=Y)
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
content_frame = CTkFrame(canvas)
canvas.create_window((0, 0), window=content_frame, anchor=NW)


# if current_date <= target_date:
# website info widgets
cookie_frame = CTkFrame(content_frame, fg_color=('#DBDBDB'))
cookie_frame.grid(pady=10, padx=20)
# label section
open = CTkButton(cookie_frame, text="Open Browser", width=130, fg_color=('#006262'),corner_radius=20, command=lambda: browser_open())
open.grid(row=1, column=0, padx=10, pady=10)

close = CTkButton(cookie_frame, text="Close Browser", width=130, fg_color=('#006262'), corner_radius=20,command=lambda: browser_close())
close.grid(row=1, column=1, padx=10, pady=10)

login_status = CTkLabel(cookie_frame,width=130, text="Login Status : False",corner_radius=20, fg_color=('#9457EB'), text_color=('#E1E8FF'))
login_status.grid(row=1, column=2, padx=10, pady=10)
if os.path.exists('storage_state.json'):
        if os.path.getsize('storage_state.json') > 0:
            login_status.configure(text='Login Status : True')

sleep_time = CTkComboBox(cookie_frame, width=100, values=["1", "3","5","8","12","15","19","25","30"], state='readonly',
                             fg_color=('black', 'white'), text_color=('white', 'black'))
sleep_time.grid(row=1, column=3, padx=10, pady=10)
sleep_time.set("Sleep")

# URL Frame
url_frame = CTkFrame(content_frame, fg_color=('#DBDBDB'), border_width=1)
url_frame.grid(pady=10, padx=20)

url_input_labe = CTkLabel(url_frame, text="URL Group Link List", font=(None,15))
url_input_labe.grid(row=2, column=0, padx=10, pady=3)
url_input = CTkTextbox(url_frame, fg_color=('black', 'white'), text_color=('white', 'black'), width=550, height=150)
url_input.insert('1.0',str(cur.execute('''SELECT url FROM Postdata WHERE ID=1''').fetchone()[0]))
url_input.grid(row=3, column=0, padx=5, pady=(5, 10))

message_labe = CTkLabel(url_frame, text="Input Post Content",font=(None,15))
message_labe.grid(row=4, column=0, padx=10, pady=3)
message = CTkTextbox(url_frame, fg_color=('black', 'white'), text_color=('white', 'black'), width=550, height=100)
message.insert('1.0',str(cur.execute('''SELECT Message FROM Postdata WHERE ID=1''').fetchone()[0]))
message.grid(row=5, column=0, padx=5, pady=(5, 10))


file_frame = CTkFrame(content_frame, border_width=1, fg_color=('#DBDBDB'))
file_frame.grid(pady=10, padx=20)
def select_file():
    file_path = filedialog.askopenfilename(title="Select a File",
                                           filetypes=[("Image", "*.png;*.jpg;*.jpeg;*.mp4;*.MOV;*.WMV")
                                                      ])
    if file_path:
        file_label.configure(text=f"{os.path.basename(file_path)}")


# Create a CTkLabel widget for displaying selected file path
file_label = CTkLabel(file_frame, text="No file selected", width=395)
file_label.grid(row=6, column=0, padx=10, pady=3)

# Create a CTkButton to trigger file selection dialog
upload_button = CTkButton(file_frame, text="Select File", command=lambda: select_file())
upload_button.grid(row=6, column=1)


# Command
command_label = CTkFrame(content_frame, fg_color=('#DBDBDB'))
command_label.grid(row=14, column=0, padx=5, pady=(30, 30))
start = CTkButton(command_label, text="▶️ Run", width=120, fg_color=('#006262'), corner_radius=20,command=lambda: operation_start())
start.grid(row=15, column=0, padx=5, pady=10, ipadx=5)
stop = CTkButton(command_label, text="⏹️ Stop", width=120, fg_color=('#9457EB'), corner_radius=20,command=lambda: operation_close())
stop.grid(row=15, column=1, padx=5, pady=10, ipadx=5)
Update = CTkButton(command_label, text='✔ Save Data', width=120, fg_color=("#006262"), corner_radius=20,command=lambda: db_save())
Update.grid(row=15, column=2, padx=5, pady=10, ipadx=5)
Reset = CTkButton(command_label, text='↻ Reset Data', width=120, fg_color=("#9457EB"), corner_radius=20,command=lambda: reset_data())
Reset.grid(row=15, column=3, padx=5, pady=10, ipadx=5)


# Log
log_label = CTkLabel(content_frame, text="Logs", font=('', 20), fg_color=("#9457EB"), text_color=('white', 'black'), corner_radius=20,)
log_label.grid(row=16, column=0, pady=0, ipadx=20)
log = CTkTextbox(content_frame, fg_color=('black', 'white'), text_color=('white', 'black'), width=550, height=200)
log.grid(row=17, column=0, padx=5, pady=(5, 10))
# else:
#     log_label = CTkLabel(content_frame, text="Trail Testing Expired..", font=('', 20))
#     log_label.grid(row=16, column=0, pady=0, ipadx=20)

copyright = CTkLabel(content_frame, text="Need any help ?", width=600)
copyright.grid(row=18, column=0, padx=5, pady=(5, 0))
copy_button = CTkButton(content_frame, text="Contact With Developer", fg_color=('#2374E1'),command=lambda: webbrowser.open_new('https://www.facebook.com/samratprodev/'))
copy_button.grid(row=19, column=0, padx=5, pady=(5, 300))


def db_save():
    get_url = str(url_input.get('1.0',END))
    get_message = str(message.get('1.0',END))



    cur.execute('''
        UPDATE Postdata
        SET
            url = ?,
            Message = ?
            
        WHERE ID = 1
    ''', (
        get_url,
        get_message

    ))


def reset_data():
    # Clear and update fields data
    url_input.delete('1.0',END)
    url_input.insert('1.0', url_db)

    message.delete('1.0',END)
    message.insert('1.0', message_db)

    # Update database
    cur.execute(f'''
                    UPDATE Postdata
                    SET
                        url = '{url_db}',
                        Message = '{message_db}',
                          
                    WHERE ID = 1

                    ''')
    # window.destroy()



browser_close_event = threading.Event()
def browser_open():
    thread = threading.Thread(target=browser_open_thread)
    thread.start()

def browser_open_thread():
    # Clear the event if the browser is being opened
    browser_close_event.clear()
    cookie_save(login_status, log, close_event=browser_close_event)
def browser_close():
    # Set the event to signal the browser should close
    browser_close_event.set()

operation_close_event = threading.Event()
def operation_start():
    start.configure(text="⌛️ Running...")
    thread = threading.Thread(target=operation_start_thread)
    thread.start()
def operation_close():
    start.configure(text="▶️ Run")
    operation_close_event.set()

def operation_start_thread():
    get_url = url_input.get('1.0',END)
    get_message = message.get('1.0', END)
    sleeping = sleep_time.get()
    get_file = file_label.cget("text")
    # print(get_url)
    # print(get_message)
    # print(get_browser_status)
    # print(get_file)
    operation_close_event.clear()
    scrapper_loop(get_url, get_message, get_file, sleeping, log, start, close_event=operation_close_event)
def on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


if __name__ == '__main__':
    window.mainloop()

con.commit()
cur.close()