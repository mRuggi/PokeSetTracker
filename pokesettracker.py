import os
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.image import Image as LogoImage
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from PIL import Image as PILImage

class PokeSetTrackerApp(App):
    def build(self):
        # Fullscreen window mode
        Window.clearcolor = (1, 1, 1, 1)
        Window.size = (1920, 1080)
        Window.borderless = False  # Windowed mode with borders

        self.card_vars = []  # Store ownership variables
        self.image_paths = []  # Store image paths
        self.completion_percentage = 0

        # Dictionary to define subsets of cards to load for buttons 2, 3, and 4
        self.subsets = {
            'button2': ['1', '2', '3'],
            'button3': ['4', '5', '6'],
            'button4': ['10']
        }

        # Main layout with vertical orientation
        main_layout = BoxLayout(orientation='vertical')

        # Add logo, centered at the top
        logo = LogoImage(source='assets/logo.png', size_hint_y=None, height='150dp')
        logo_layout = BoxLayout(size_hint_y=None, height='180dp')  # To center the logo
        logo_layout.add_widget(logo)
        main_layout.add_widget(logo_layout)

        # Toolbar with buttons below the logo
        toolbar = BoxLayout(size_hint_y=None, height='100dp', spacing=10, padding=[10, 20, 10, 20])
        main_layout.add_widget(toolbar)

        # Add four buttons with images from assets
        button_names = ['button1', 'button2', 'button3', 'button4']
        for name in button_names:
            btn = Button(
                background_normal=f'assets/{name}.png',
                size_hint=(None, None), 
                size=(151, 71)  # Set button size to 151x71 pixels
            )
            if name == 'button1':
                btn.bind(on_release=lambda instance: self.load_images_from_directory())  # Load all cards
            elif name == 'button2':
                btn.bind(on_release=lambda instance: self.load_subset('button2'))
            elif name == 'button3':
                btn.bind(on_release=lambda instance: self.load_subset('button3'))
            elif name == 'button4':
                btn.bind(on_release=lambda instance: self.load_subset('button4'))

            toolbar.add_widget(btn)

        # Scrollable area for card images, with 10 columns to make images more visible
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.cards_layout = GridLayout(cols=5, spacing=30, size_hint_y=None)
        self.cards_layout.bind(minimum_height=self.cards_layout.setter('height'))
        self.scroll_view.add_widget(self.cards_layout)
        main_layout.add_widget(self.scroll_view)

        # Bottom toolbar with Load, Save, and Quit buttons
        bottom_toolbar = BoxLayout(size_hint_y=None, height='80dp', padding=10, spacing=10)

        load_btn = Button(text='Load', size_hint=(None, None), size=(151, 71))
        load_btn.bind(on_release=self.load_state)
        bottom_toolbar.add_widget(load_btn)

        save_btn = Button(text='Save', size_hint=(None, None), size=(151, 71))
        save_btn.bind(on_release=self.save_state)
        bottom_toolbar.add_widget(save_btn)

        quit_btn = Button(text='Quit', size_hint=(None, None), size=(151, 71))
        quit_btn.bind(on_release=self.stop)
        bottom_toolbar.add_widget(quit_btn)

        # Completion percentage label
        self.completion_label = Label(text="Completion: 0%", size_hint_y=None, height='50dp', color=(0, 0, 0, 1))
        bottom_toolbar.add_widget(self.completion_label)

        main_layout.add_widget(bottom_toolbar)

        # Load images from the specified directory
        self.load_images_from_directory()

        return main_layout

    def load_images_from_directory(self, subset_filters=None):
        # Clear previous images
        self.cards_layout.clear_widgets()
        self.image_paths.clear()
        self.card_vars.clear()

        # Define the directory to load images from
        directory = 'genetic_apex_cards'

        # Check if the directory exists
        if not os.path.exists(directory):
            popup = Popup(title="Error", content=Label(text=f"Directory '{directory}' not found."), size_hint=(0.5, 0.5))
            popup.open()
            return

        # Loop through the directory and load images
        for filename in os.listdir(directory):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):  # Check for image files
                if subset_filters:
                    # Load only if the filename starts with one of the subset filters
                    if any(filename.startswith(f"{filter}-") for filter in subset_filters):
                        self.image_paths.append(os.path.join(directory, filename))
                else:
                    self.image_paths.append(os.path.join(directory, filename))

        # Sort images using custom sort
        self.image_paths.sort(key=self.custom_sort_key)

        # Load and display all images
        self.load_all_images()

    def custom_sort_key(self, image_path):
        base_name = os.path.basename(image_path)
        match = re.match(r"(\d+)-?(.*)", base_name)
        if match:
            number = int(match.group(1))
            name = match.group(2).lower()
            return (number, name)
        return (float('inf'), base_name)

    def load_all_images(self):
        for image_path in self.image_paths:
            img_texture = self.load_image(image_path)
            if img_texture is not None:
                # Create a card for the image
                card_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=img_texture.height + 50)  # Add height for checkbox and label

                img = Image(texture=img_texture, size_hint=(None, None), size=(img_texture.width, img_texture.height))
                card_layout.add_widget(img)

                checkbox_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing=0)  
                card_var = CheckBox(size_hint=(None, None), width='50dp', height='50dp')  # You can reduce the size if needed
                card_var.bind(active=self.update_completion)

                filename = os.path.basename(image_path).split('.')[0]
                card_name = re.sub(r'^\d+-|-\d+x\d+', '', filename).capitalize()
                card_label = Label(text=card_name, size_hint_y=None, height='50dp', color=(0, 0, 0, 1), size_hint_x=None, width=200)  # Adjust width as needed

                checkbox_layout.add_widget(card_var)
                checkbox_layout.add_widget(card_label)

                card_layout.add_widget(checkbox_layout)

                self.cards_layout.add_widget(card_layout)
                self.card_vars.append(card_var)

        self.update_completion()  # Update completion after loading images

    def load_image(self, image_path):
        try:
            img = PILImage.open(image_path)
            img_data = img.tobytes()
            texture = Texture.create(size=img.size, colorfmt='rgba')
            texture.blit_buffer(img_data, colorfmt='rgba', bufferfmt='ubyte')
            texture.flip_vertical()  # Flip the texture to fix flipped images
            return texture
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None

    def load_subset(self, button_key):
        subset_filters = self.subsets.get(button_key, [])
        self.load_images_from_directory(subset_filters)

    def update_completion(self, instance=None, value=None):
        owned_cards = [var.active for var in self.card_vars]
        if self.card_vars:
            self.completion_percentage = sum(owned_cards) / len(self.card_vars) * 100
            self.completion_label.text = f"Completion: {self.completion_percentage:.2f}%"
        else:
            self.completion_label.text = "Completion: 0%"

    def save_state(self, instance):
        try:
            with open('data.txt', 'w') as f:
                for var in self.card_vars:
                    f.write(f"{int(var.active)}\n")
                f.write(f"Completion: {self.completion_percentage:.2f}%\n")
            popup = Popup(title="Success", content=Label(text="State saved successfully."), size_hint=(0.5, 0.5))
            popup.open()
        except Exception as e:
            popup = Popup(title="Error", content=Label(text=f"Error saving state: {e}"), size_hint=(0.5, 0.5))
            popup.open()

    def load_state(self, instance):
        try:
            with open('data.txt', 'r') as f:
                lines = f.readlines()
                for i, var in enumerate(self.card_vars):
                    var.active = bool(int(lines[i].strip()))
                self.update_completion()
            popup = Popup(title="Success", content=Label(text="State loaded successfully."), size_hint=(0.5, 0.5))
            popup.open()
        except Exception as e:
            popup = Popup(title="Error", content=Label(text=f"Error loading state: {e}"), size_hint=(0.5, 0.5))
            popup.open()

if __name__ == '__main__':
    PokeSetTrackerApp().run()
