# Nathan Fitzgerald
# Student Number- x20777665
# Student Email- x20777665@student.ncirl.ie
import easyocr
import customtkinter
import requests
import cv2
from tkinter import messagebox
from PIL import Image, ImageTk


# Reference-
# https://scryfall.com/docs/api
# https://www.youtube.com/watch?v=MvzK9Oguxcg&ab_channel=Atlas
# https://www.youtube.com/watch?v=U23M379YId8&ab_channel=Atlas
# https://www.youtube.com/watch?v=hpc5jyVpUpw&ab_channel=AaronJack
# https://www.youtube.com/watch?v=4en9gSwmn5g&t=129s&ab_channel=Atlas
# https://www.youtube.com/watch?v=ON_JubFRw8M&ab_channel=Murtaza%27sWorkshop-RoboticsandAI
# https://www.youtube.com/watch?v=PY_N1XdFp4w&ab_channel=NeuralNine
# https://www.youtube.com/watch?v=JSv42fF-tU4&ab_channel=CodingShiksha
# https://www.youtube.com/watch?v=YUknIYLXS1s&t=33s&ab_channel=Adi%27sTechnicalAid
# https://www.youtube.com/watch?v=YIdy3sqGGvs&ab_channel=TheAiGenomewithSakshamJain
# https://note.nkmk.me/en/python-opencv-bgr-rgb-cvtcolor/

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")
SCRYFALL_API_BASE = "https://api.scryfall.com/cards/search"

window = customtkinter.CTk()
window.geometry('1000x500')
window.title("Tab Widget")


class ScanMTG:
    def __init__(self):

        self.cap = None
        self.camera_on = False
        notebook = customtkinter.CTkTabview(window)
        notebook.pack()

        # Tab 1
        notebook.add('Camera')
        # Tab 2
        notebook.add('Card Reader')

        # Tab 1 / Camera Tab

        self.canvas = customtkinter.CTkCanvas(notebook.tab('Camera'), width=800, height=600)
        self.canvas.pack()

        button_on = customtkinter.CTkButton(notebook.tab('Camera'), text='Turn On', command=self.turn_on_camera)
        button_on.pack(pady=12, padx=10)
        # Has a weird gap between button_on and button_off.
        # Wasn't there in earlier versions. Might be related to canvas?

        button_off = customtkinter.CTkButton(notebook.tab('Camera'), text='Turn Off', command=self.turn_off_camera)
        button_off.pack(pady=12, padx=10)

        take_photo_button = customtkinter.CTkButton(notebook.tab('Camera'), text="Take Photo", command=self.take_photo)
        take_photo_button.pack()

        # Tab 2 / Card Reader Tab
        self.name_label = customtkinter.CTkLabel(notebook.tab('Card Reader'), text='Card Name: No text detected.',
                                                 font=("Roboto", 24))
        self.name_label.pack(pady=40, padx=20)

        self.image_label = customtkinter.CTkLabel(notebook.tab('Card Reader'), text='')
        self.image_label.pack(pady=10)

        self.value_label = customtkinter.CTkLabel(notebook.tab('Card Reader'), text='Value: No text detected.',
                                                  font=("Roboto", 24))
        self.value_label.pack(pady=40, padx=20)

        button_process = customtkinter.CTkButton(notebook.tab('Card Reader'), text='Process Image',
                                                 command=self.process_image)
        button_process.pack(pady=12, padx=10)

        button_price = customtkinter.CTkButton(notebook.tab('Card Reader'), text='Valuate Price',
                                               command=self.find_price)
        button_price.pack(pady=12, padx=10)

        window.mainloop()

    # Image Processor Code
    def process_image(self):
        IMAGE_PATH = ("magic_card.jpg")

        if not IMAGE_PATH:
            return

        reader = easyocr.Reader(['en'], gpu=False)
        results = reader.readtext(IMAGE_PATH)

        card_name = None

        for result in results:
            text = result[1]
            if card_name is None:
                card_name = text
                break

        if card_name is None:
            self.name_label.configure(text='Card Name: No text detected.')
        else:
            self.name_label.configure(text=f'Card Name: {card_name}')

        img = Image.open(IMAGE_PATH)
        img.thumbnail((400, 400))
        img = ImageTk.PhotoImage(img)
        self.image_label.configure(image=img)
        self.image_label.image = img

    # Api Searcher Code
    def find_price(self):
        card_name = self.name_label.cget("text").replace("Card Name: ", "")
        if card_name == "No text detected.":
            return
# set card's name and sends request.get
        params = {"q": f'name:"{card_name}"'}
        response = requests.get(SCRYFALL_API_BASE, params=params)
# Checks if Api is functioning and retrieve card's price
        if response.status_code == 200:
            data = response.json()
            if data['object'] == 'error':
                print("Card not found.")
            else:
                card = data['data'][0]
                if 'usd' in card['prices']:
                    price = card['prices']['usd']
                    print(f"The price of {card_name} is ${price}.")
                else:
                    print("Price not available for this card.")
        else:
            print("Failed to retrieve card information.")
# Updates value_label with Card's Value
        if price is None:
            self.value_label.configure(text='Card Value: No text detected.')
        else:
            self.value_label.configure(text=f'Card Market Value: ${price}', )

    # Camera Code Section / Everything below is related to Camera Functionality
    def update_camera(self):
        if self.camera_on:
            ret, frame = self.cap.read()
            if ret:
                # Convert the images into RGB, and resizes it to 800, 600
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (800, 600))

                # Convert the Image to a PIL image
                img = Image.fromarray(frame)
                img = ImageTk.PhotoImage(img)

                # Updates canvas with the new image
                self.canvas.create_image(0, 0, anchor=customtkinter.NW, image=img)
                self.canvas.img = img

            # Updates Canvas After 10 milliseconds
            self.canvas.after(10, self.update_camera)
    def take_photo(self):
        if not self.camera_on:
            messagebox.showwarning("Camera Not Turned On", "Please turn on the camera first.")
            return

        ret, frame = self.cap.read()
        if ret:
            # Save the photo with a white outline (To simulate the area where a Card from MTG should be placed)
            # Needs re-writing, saves image with a white frame instead of displaying
            # a rectangle frame in the webcam feed as it should
            magic_card = cv2.rectangle(frame, (100, 100), (500, 700), (255, 255, 255), 2)
            cv2.imwrite("magic_card.jpg", magic_card)
            messagebox.showinfo("Photo Taken", "The photo has been saved as 'magic_card.jpg'")
            ScanMTG.quit()
        else:
            messagebox.showerror("Error", "Failed to capture photo!")

    # Function to turn on the camera
    def turn_on_camera(self):
        if not self.camera_on:
            self.cap = cv2.VideoCapture(0)  # Starts the camera
            self.camera_on = True
            self.update_camera()

    # Function to turn off the camera
    def turn_off_camera(self):
        if self.camera_on:
            # Turns off the camera
            self.cap.release()
            self.camera_on = False
            self.canvas.delete("all")  # Clear the canvas, resetting canvas for next turn on
            
            
if __name__ == '__main__':
    ScanMTG()
