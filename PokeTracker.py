import os
import re
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Function to load a specific image given its path
def load_image(image_path, size=(150, 210)):
    try:
        img = Image.open(image_path)
        img.thumbnail(size, Image.LANCZOS)  # Resize keeping aspect ratio
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")  # Debugging line
        return None

# Function to load images from the specified directory
def load_images_from_directory(directory):
    global image_paths
    image_paths = []  # Clear previous paths

    # List to store card variables for checkboxes
    global card_vars
    card_vars.clear()

    # Loop through all files in the specified directory
    for filename in os.listdir(directory):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):  # Check for image files
            image_paths.append(os.path.join(directory, filename))  # Save image path

    # Sort image paths using custom sort function
    image_paths.sort(key=custom_sort_key)

    # Load all images at once
    load_all_images()

# Custom sort key function
def custom_sort_key(image_path):
    # Extracting number and name from the filename
    base_name = os.path.basename(image_path)  # Get filename from path
    match = re.match(r"(\d+)-?(.*)", base_name)  # Match pattern "number_name"
    if match:
        number = int(match.group(1))  # Extract number
        name = match.group(2).lower()  # Extract name and convert to lowercase for sorting
        return (number, name)  # Return a tuple (number, name) for sorting
    return (float('inf'), base_name)  # In case of no match, send to end

# Function to load all images for display
def load_all_images():
    # Clear current card display
    for widget in cards_frame.winfo_children():
        widget.destroy()

    # Load and display all images
    for count, image_path in enumerate(image_paths):
        load_card_image(image_path, count)  # Load and display image

    # Reset completion label
    update_completion()

# Function to load a card image and display it
def load_card_image(image_path, count):
    img = load_image(image_path)  # Load image
    if img is not None:
        # Create a frame for each card
        card_frame = ttk.Frame(cards_frame)
        card_frame.grid(row=count // 8, column=count % 8, padx=10, pady=10)  # 8 cards per row

        # Create label to display image
        img_label = tk.Label(card_frame, image=img)
        img_label.image = img  # Keep reference to avoid garbage collection
        img_label.pack()

        # Create checkbutton for ownership tracking
        card_var = tk.IntVar()
        checkbutton = ttk.Checkbutton(
            card_frame, variable=card_var, command=update_completion
        )
        checkbutton.pack()

        # Store the variable reference for future tracking
        card_vars.append(card_var)

# Function to update the completion percentage
def update_completion():
    owned_cards = [var.get() for var in card_vars]
    if card_vars:
        completion_percentage = sum(owned_cards) / len(card_vars) * 100
        completion_label.config(text=f"Completion: {completion_percentage:.2f}%")
    else:
        completion_label.config(text="Completion: 0%")

# Function to handle button actions
def button_one_action():
    print("Button 1 clicked")

def button_two_action():
    print("Button 2 clicked")

def button_three_action():
    print("Button 3 clicked")

def button_four_action():
    print("Button 4 clicked")

# Function to handle Save button action
def save_action():
    try:
        with open('data.txt', 'w') as f:
            # Save the state of each checkbox
            for var in card_vars:
                f.write(f"{var.get()}\n")
            # Save the completion percentage
            completion_percentage = completion_label.cget("text").split(': ')[1]
            f.write(f"Completion: {completion_percentage}\n")
        print("State saved successfully.")
    except Exception as e:
        print(f"Error saving state: {e}")

# Function to handle Load button action
def load_action():
    try:
        with open('data.txt', 'r') as f:
            # Read the state of each checkbox
            for i, line in enumerate(f):
                if i < len(card_vars):
                    card_vars[i].set(int(line.strip()))  # Set checkbox state
            # Read the completion percentage (if needed)
            completion_line = line.strip()  # Get last line for completion
            completion_label.config(text=completion_line)  # Update label
        update_completion()  # Recalculate completion percentage
        print("State loaded successfully.")
    except Exception as e:
        print(f"Error loading state: {e}")

# Initialize main window
root = tk.Tk()
root.title("PokéSet Tracker")

# Set to windowed fullscreen (cover the entire screen with window decorations)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}+0+0")  # Fullscreen size
root.overrideredirect(False)  # Allow window decorations

# Create a frame for the toolbar
toolbar_frame = ttk.Frame(root)
toolbar_frame.pack(side=tk.TOP, fill=tk.X)

# Load button images with maintained aspect ratio
button_images = {}
def load_button_image(name):
    img_path = f"assets/{name}.png"
    img = Image.open(img_path)
    img.thumbnail((50, 50), Image.LANCZOS)  # Maintain aspect ratio
    return ImageTk.PhotoImage(img)

button_images['button1'] = load_button_image('button1')
button_images['button2'] = load_button_image('button2')
button_images['button3'] = load_button_image('button3')
button_images['button4'] = load_button_image('button4')

# Add buttons to the toolbar with images
button1 = ttk.Button(toolbar_frame, image=button_images['button1'], command=button_one_action)
button1.pack(side=tk.LEFT, padx=5, pady=5)

button2 = ttk.Button(toolbar_frame, image=button_images['button2'], command=button_two_action)
button2.pack(side=tk.LEFT, padx=5, pady=5)

button3 = ttk.Button(toolbar_frame, image=button_images['button3'], command=button_three_action)
button3.pack(side=tk.LEFT, padx=5, pady=5)

button4 = ttk.Button(toolbar_frame, image=button_images['button4'], command=button_four_action)
button4.pack(side=tk.LEFT, padx=5, pady=5)

# Load the logo image
logo_image_path = "assets/logo.png"  # Adjust the filename if needed
logo_image = Image.open(logo_image_path)
logo_image.thumbnail((200, 100), Image.LANCZOS)  # Resize as needed
logo_photo = ImageTk.PhotoImage(logo_image)

# Create a label to display the logo
logo_label = ttk.Label(root, image=logo_photo)
logo_label.pack(pady=10)

# Completion Percentage Label (near the buttons)
completion_label = ttk.Label(toolbar_frame, text="Completion: 0%", font=("Arial", 12))
completion_label.pack(side=tk.LEFT, padx=10)  # Added next to buttons

# Create a canvas and a scrollbar
canvas = tk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

# Configure the scrollable frame
scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Create a window in the canvas
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

# Add scrollbar to the canvas
canvas.configure(yscrollcommand=scrollbar.set)

# Pack the canvas and scrollbar
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Frame to hold the cards list
cards_frame = ttk.Frame(scrollable_frame)
cards_frame.pack(pady=10)

# Store card ownership variables
card_vars = []

# Quit Button (aligned to bottom right)
quit_button = ttk.Button(root, text="Quit", command=root.quit)
quit_button.pack(side=tk.BOTTOM, anchor='se', padx=10, pady=10)  # Place it at the bottom right

# Save Button (aligned to bottom right, next to quit button)
save_button = ttk.Button(root, text="Save", command=save_action)
save_button.pack(side=tk.BOTTOM, anchor='se', padx=10, pady=(10, 5))  # Place it at the bottom right, above quit

# Load Button (aligned to bottom right, next to quit button)
load_button = ttk.Button(root, text="Load", command=load_action)
load_button.pack(side=tk.BOTTOM, anchor='se', padx=10, pady=(5, 10))  # Place it at the bottom right, above save

# Load images from the specified directory
load_images_from_directory('genetic_apex_cards')  # Use the path where your images are stored

# Start the Tkinter event loop
root.mainloop()
