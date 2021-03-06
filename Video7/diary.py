"""My Diary Application in Tkinter"""
import tkinter as tk
from tkinter import messagebox as tkmb
from tkinter import simpledialog as tksd
from tkinter import filedialog as tkfd
from pathlib import Path
from datetime import datetime

# First line
root = tk.Tk()
font_size = tk.IntVar(value=12)

# configure root
root.title('My Diary')
root.geometry('800x600+300+300')
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.configure(bg='#888')

# Sub-frame for form
form_frame = tk.Frame(root)
form_frame.grid(sticky=tk.N + tk.E + tk.W + tk.S, padx=5, pady=5)
form_frame.columnconfigure(0, weight=1)
form_frame.rowconfigure(5, weight=1)

# subject
subj_frame = tk.Frame(form_frame)
subj_frame.columnconfigure(1, weight=1)
subject_var = tk.StringVar()
tk.Label(
    subj_frame,
    text='Subject: '
).grid(sticky='we', padx=5, pady=5)
tk.Entry(
    subj_frame,
    textvariable=subject_var
).grid(row=0, column=1, sticky=tk.E + tk.W)
subj_frame.grid(sticky='ew')

# category
cat_frame = tk.Frame(form_frame)
cat_frame.columnconfigure(1, weight=1)
cat_var = tk.StringVar()
categories = ['Work', 'Hobbies', 'Health', 'Bills']
tk.Label(
    cat_frame,
    text='Category: '
).grid(sticky=tk.E + tk.W, padx=5, pady=5)
tk.OptionMenu(
    cat_frame,
    cat_var,
    *categories
).grid(row=0, column=1, sticky=tk.E + tk.W, padx=5)
cat_frame.grid(sticky='ew')

# Private
private_var = tk.BooleanVar(value=False)
tk.Checkbutton(
    form_frame,
    variable=private_var,
    text='Private?'
).grid(ipadx=5, ipady=2, sticky='w')

# Datestamp
datestamp_var = tk.StringVar(value='none')
datestamp_frame = tk.Frame(form_frame)
for value in ('None', 'Date', 'Date+Time'):
    tk.Radiobutton(
        datestamp_frame,
        text=value,
        value=value,
        variable=datestamp_var
    ).pack(side=tk.LEFT)
datestamp_frame.grid(row=2, sticky='e')

# message
message_frame = tk.LabelFrame(form_frame, text='Message')
message_frame.columnconfigure(0, weight=1)
message_frame.rowconfigure(0, weight=1)
message_inp = tk.Text(message_frame)
message_inp.grid(sticky='nesw')

scrollbar = tk.Scrollbar(message_frame)
scrollbar.grid(row=0, column=1, sticky='nse')
message_frame.grid(row=5, sticky='nsew')
scrollbar.configure(command=message_inp.yview)
message_inp.configure(yscrollcommand=scrollbar.set)

# save button
save_btn = tk.Button(
    form_frame,
    text='Save'
)
save_btn.grid(sticky=tk.E, ipadx=5, ipady=5)

# open button
#open_btn = tk.Button(
#    root,
#    text='Open'
#)
#open_btn.grid(sticky=tk.E, ipadx=5, ipady=5)

# Status bar
status_var = tk.StringVar()
tk.Label(
    root,
    textvariable=status_var
).grid(row=100, ipadx=5, ipady=5, padx=5, pady=5, sticky='we')

# Functions and bindings
def weaksauce_encrypt(text, password):
    """Weakly and insecurely encrypt some text"""

    offset = sum([ord(x) for x in password])
    encoded = ''.join(
        chr(min(ord(x) + offset, 2**20))
        for x in text
    )
    return encoded

def weaksauce_decrypt(text, password):
    """Decrypt weakly and insecurely encrypted text"""
    offset = sum([ord(x) for x in password])
    decoded = ''.join(
        chr(max(ord(x) - offset, 0))
        for x in text
    )
    return decoded

def open_file():
    """Open a diary file"""

    file_path = tkfd.askopenfilename(
        title='Select a file to open',
        filetypes=[('Secret', '*.secret'), ('Text', "*.txt")],
    )
    if not file_path:
        return
    fp = Path(file_path)
    filename = fp.stem
    category, subject = filename.split(' - ')
    message = fp.read_text()
    if fp.suffix == '.secret':
        password = tksd.askstring(
            'Enter Password',
            'Enter the password used to '
            'encrypt the file.'
        )
        message = weaksauce_decrypt(message, password)

    cat_var.set(category)
    subject_var.set(subject)
    message_inp.delete('1.0', tk.END)
    message_inp.insert('1.0', message)

#open_btn.configure(command=open_file)

def save():
    """Save the data to a file"""

    subject = subject_var.get()
    category = cat_var.get()
    private = private_var.get()
    message = message_inp.get('1.0', tk.END)
    datestamp_type = datestamp_var.get()

    extension = 'txt' if not private else 'secret'
    filename = f'{category} - {subject}.{extension}'

    # Apply optional datestamp in message
    if datestamp_type == 'Date':
        datestamp = datetime.today().strftime('%Y-%m-%d')
    elif datestamp_type == 'Date+Time':
        datestamp = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
    else:
        datestamp = ''
    if datestamp:
        message = f'{message}\n\n{datestamp}'

    if private:
        password = tksd.askstring(
            'Enter password',
            'Enter a password to encrypt the message.'
        )
        message = weaksauce_encrypt(message, password)

    with open(filename, 'w') as fh:
        fh.write(message)

    status_var.set(f'Message was saved to {filename}')
    tkmb.showinfo('Saved', f'Message was saved to {filename}')

save_btn.configure(command=save)

def private_warn(*arg):
    """Warn the user about the consequences of private"""
    private = private_var.get()

    if private:
        response = tkmb.askokcancel(
            "Are you sure?",
            "Do you really want to encrypt this message?"
        )
        if not response:
            private_var.set(False)

private_var.trace_add('write', private_warn)


def check_filename(*args):
    """Check if a filename is already in use"""
    subject = subject_var.get()
    category = cat_var.get()
    private = private_var.get()

    extension = 'txt' if not private else 'secret'
    filename = f'{category} - {subject}.{extension}'

    if Path(filename).exists():
        status_var.set(f'WARNING: {filename} already exists!')
    else:
        status_var.set('')

subject_var.trace_add('write', check_filename)
cat_var.trace_add('write', check_filename)
private_var.trace_add('write', check_filename)

def set_font_size(*args):
    """Set the size of the text widget font from font_size"""
    size = font_size.get()
    message_inp.configure(font=f'TKDefault {size}')

set_font_size()
font_size.trace_add('write', set_font_size)

# Menu

menu = tk.Menu(root)
root.configure(menu=menu)

file_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label='File', menu=file_menu)
file_menu.add_command(label='Open', command=open_file)
file_menu.add_command(label='Save', command=save)
file_menu.add_separator()
file_menu.add_command(label='Quit', command=root.destroy)

options_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label='Options', menu=options_menu)
options_menu.add_checkbutton(label='Private', variable=private_var)

help_menu = tk.Menu(menu, tearoff=0)
help_menu.add_command(
    label='About',
    command=lambda: tkmb.showinfo('About', 'My Tkinter Diary')
)
menu.add_cascade(label='Help', menu=help_menu)

size_menu = tk.Menu(options_menu, tearoff=0)
for size in range(6, 33, 2):
    size_menu.add_radiobutton(label=size, value=size, variable=font_size)

options_menu.add_cascade(menu=size_menu, label='Font Size')



# Last line

root.mainloop()
