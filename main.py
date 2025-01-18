import cv2
import numpy as np
from tkinter import Tk, filedialog, Button, Label, Canvas, Scale, HORIZONTAL, Frame
from tkinter import ttk
from PIL import Image, ImageTk

def adjust_brightness(image, brightness=50):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.add(v, brightness)
    v = np.clip(v, 0, 255)
    final_hsv = cv2.merge((h, s, v))
    bright_image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return bright_image

def adjust_contrast(image, contrast=1.0):
    alpha = contrast
    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=0)
    return adjusted

def apply_color_filter(image, filter_type='sepia'):
    if filter_type == 'sepia':
        kernel = np.array([[0.393, 0.769, 0.189],
                           [0.349, 0.686, 0.168],
                           [0.272, 0.534, 0.131]])
        image = cv2.transform(image, kernel)
        image = np.clip(image, 0, 255)
    elif filter_type == 'bw':
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image

def crop_and_resize(image, x, y, w, h, new_width, new_height):
    cropped_image = image[y:y+h, x:x+w]
    resized_image = cv2.resize(cropped_image, (new_width, new_height))
    return resized_image

class PhotoEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Trình Chỉnh Sửa Ảnh")

        # Title Label
        self.title_label = Label(self.root, text="Bộ lọc phong cách cá nhân", font=("Helvetica", 20, "bold"), fg="blue")
        self.title_label.pack(pady=10)

        # Frame for controls
        self.control_frame = Frame(self.root)
        self.control_frame.pack(side="top", fill="x", padx=10, pady=5)

        self.canvas = Canvas(self.root, width=800, height=600, bg="lightgray")
        self.canvas.pack(pady=20)

        self.label = Label(self.root, text="Chọn ảnh để bắt đầu", font=("Arial", 16))
        self.label.pack(pady=5)

        # Open image button with icon and style
        self.btn_open = Button(self.control_frame, text="Mở ảnh", command=self.open_image, relief="raised", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white")
        self.btn_open.grid(row=0, column=0, padx=10, pady=5)

        # Brightness controls
        self.btn_brightness = Button(self.control_frame, text="Chỉnh sáng", command=self.apply_brightness, relief="raised", font=("Arial", 12, "bold"), bg="#FFC107", fg="black")
        self.btn_brightness.grid(row=0, column=1, padx=10, pady=5)

        self.brightness_slider = Scale(self.control_frame, from_=0, to=100, orient=HORIZONTAL, label="Độ sáng", relief="sunken", sliderlength=20)
        self.brightness_slider.set(50)
        self.brightness_slider.grid(row=0, column=2, padx=10, pady=5)

        # Contrast controls
        self.btn_contrast = Button(self.control_frame, text="Chỉnh độ tương phản", command=self.apply_contrast, relief="raised", font=("Arial", 12, "bold"), bg="#FFC107", fg="black")
        self.btn_contrast.grid(row=0, column=3, padx=10, pady=5)

        self.contrast_slider = Scale(self.control_frame, from_=0.1, to=2.0, orient=HORIZONTAL, resolution=0.1, label="Độ tương phản", relief="sunken", sliderlength=20)
        self.contrast_slider.set(1.0)
        self.contrast_slider.grid(row=0, column=4, padx=10, pady=5)

        # Filter buttons
        self.btn_sepia = Button(self.control_frame, text="Sepia", command=lambda: self.apply_color_filter('sepia'), relief="raised", font=("Arial", 12, "bold"), bg="#8E44AD", fg="white")
        self.btn_sepia.grid(row=1, column=0, padx=10, pady=5)

        self.btn_bw = Button(self.control_frame, text="Đen Trắng", command=lambda: self.apply_color_filter('bw'), relief="raised", font=("Arial", 12, "bold"), bg="#8E44AD", fg="white")
        self.btn_bw.grid(row=1, column=1, padx=10, pady=5)

        # Crop and resize button
        self.btn_crop_resize = Button(self.control_frame, text="Cắt & Resize", command=self.apply_crop_resize, relief="raised", font=("Arial", 12, "bold"), bg="#3498DB", fg="white")
        self.btn_crop_resize.grid(row=1, column=2, padx=10, pady=5)

        # Undo button
        self.btn_undo = Button(self.control_frame, text="Hoàn tác", command=self.undo, relief="raised", font=("Arial", 12, "bold"), bg="#F39C12", fg="white")
        self.btn_undo.grid(row=1, column=3, padx=10, pady=5)

        # Save button
        self.btn_save = Button(self.control_frame, text="Lưu ảnh", command=self.save_image, relief="raised", font=("Arial", 12, "bold"), bg="#27AE60", fg="white")
        self.btn_save.grid(row=1, column=4, padx=10, pady=5)

        self.image = None
        self.display_image = None
        self.history = []  # Lưu lại lịch sử ảnh để hoàn tác

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.image = cv2.imread(file_path)
            self.history = [self.image.copy()]  # Lưu ảnh gốc vào lịch sử
            self.display_image_on_canvas()

    def save_image(self):
        if self.image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
            if file_path:
                cv2.imwrite(file_path, self.image)

    def apply_brightness(self):
        if self.image is not None:
            brightness = self.brightness_slider.get()
            self.image = adjust_brightness(self.image, brightness-50)  # Adjusting slider range
            self.history.append(self.image.copy())  # Lưu lại lịch sử ảnh
            self.display_image_on_canvas()

    def apply_contrast(self):
        if self.image is not None:
            contrast = self.contrast_slider.get()
            self.image = adjust_contrast(self.image, contrast)
            self.history.append(self.image.copy())  # Lưu lại lịch sử ảnh
            self.display_image_on_canvas()

    def apply_color_filter(self, filter_type):
        if self.image is not None:
            self.image = apply_color_filter(self.image, filter_type)
            self.history.append(self.image.copy())  # Lưu lại lịch sử ảnh
            self.display_image_on_canvas()

    def apply_crop_resize(self):
        if self.image is not None:
            # Crop and Resize: Select a portion and resize
            self.image = crop_and_resize(self.image, 50, 50, 100, 100, 200, 200)
            self.history.append(self.image.copy())  # Lưu lại lịch sử ảnh
            self.display_image_on_canvas()

    def undo(self):
        if len(self.history) > 1:
            self.history.pop()  # Loại bỏ ảnh hiện tại khỏi lịch sử
            self.image = self.history[-1]  # Quay lại ảnh trước đó
            self.display_image_on_canvas()

    def display_image_on_canvas(self):
        if self.image is not None:
            image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            image_pil = Image.fromarray(image_rgb)
            self.display_image = ImageTk.PhotoImage(image_pil)
            self.canvas.create_image(400, 300, image=self.display_image, anchor="center")

if __name__ == "__main__":
    root = Tk()
    app = PhotoEditor(root)
    root.mainloop()
