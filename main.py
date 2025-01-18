import cv2
import numpy as np
from tkinter import Tk, filedialog, Button, Label, Canvas, Scale, HORIZONTAL, Frame, Toplevel
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt

# Các hàm xử lý ảnh (tính năng cũ)
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
# Bộ lọc Luminous: Tăng cường độ sáng và làm sáng da
def apply_luminous_filter(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.add(v, 50)  # Tăng độ sáng
    v = np.clip(v, 0, 255)
    final_hsv = cv2.merge((h, s, v))
    luminous_image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return luminous_image

# Bộ lọc Glowing: Tạo hiệu ứng phát sáng
def apply_glowing_filter(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.add(v, 100)  # Tăng độ sáng lên mạnh mẽ
    s = cv2.multiply(s, 1.2)  # Tăng cường độ bão hòa màu
    v = np.clip(v, 0, 255)
    s = np.clip(s, 0, 255)
    final_hsv = cv2.merge((h, s, v))
    glowing_image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return glowing_image

# Bộ lọc Vintage: Tạo hiệu ứng cổ điển với tông màu ấm
def apply_vintage_filter(image):
    kernel = np.array([[0.393, 0.769, 0.189],
                       [0.349, 0.686, 0.168],
                       [0.272, 0.534, 0.131]])
    vintage_image = cv2.transform(image, kernel)
    vintage_image = np.clip(vintage_image, 0, 255)
    return vintage_image

# Bộ lọc Neon: Tạo hiệu ứng sáng neon
def apply_neon_filter(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    s = cv2.multiply(s, 1.5)  # Tăng độ bão hòa mạnh mẽ
    v = cv2.add(v, 50)  # Tăng độ sáng mạnh mẽ
    s = np.clip(s, 0, 255)
    v = np.clip(v, 0, 255)
    final_hsv = cv2.merge((h, s, v))
    neon_image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return neon_image
# Hàm xoá phông
def remove_background(image):
    # Chuyển ảnh từ BGR sang HSV để dễ dàng xử lý
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Định nghĩa khoảng màu nền (ví dụ màu xanh lá cây)
    lower_bound = np.array([35, 50, 50])  # Màu xanh lá cây (HSV)
    upper_bound = np.array([85, 255, 255])

    # Tạo mặt nạ để giữ lại các phần không phải là nền
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Đảo ngược mặt nạ để lấy phần không phải là nền
    mask_inv = cv2.bitwise_not(mask)

    # Lọc phần không phải là nền từ ảnh gốc
    result = cv2.bitwise_and(image, image, mask=mask_inv)
    
    return result

# Hàm tính toán và vẽ biểu đồ màu cục bộ
def compute_local_color_histogram(image, x, y, width, height):
    region = image[y:y+height, x:x+width]
    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    
    h_hist = cv2.calcHist([hsv], [0], None, [256], [0, 256])  # Hue
    s_hist = cv2.calcHist([hsv], [1], None, [256], [0, 256])  # Saturation
    v_hist = cv2.calcHist([hsv], [2], None, [256], [0, 256])  # Value
    
    return h_hist, s_hist, v_hist

def show_local_color_histogram(image, x, y, width, height):
    h_hist, s_hist, v_hist = compute_local_color_histogram(image, x, y, width, height)
    
    # Vẽ biểu đồ
    plt.figure(figsize=(10, 5))
    
    plt.subplot(131)
    plt.plot(h_hist, color='r')
    plt.title('Hue Histogram')
    
    plt.subplot(132)
    plt.plot(s_hist, color='g')
    plt.title('Saturation Histogram')
    
    plt.subplot(133)
    plt.plot(v_hist, color='b')
    plt.title('Value Histogram')
    
    plt.tight_layout()
    plt.show()

class PhotoEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Bộ lọc ảnh AI")

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

        # Nút mở ảnh với biểu tượng và kiểu dáng
        self.btn_open = Button(self.control_frame, text="Mở ảnh", command=self.open_image, relief="raised", font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="black")
        self.btn_open.grid(row=0, column=0, padx=10, pady=5)

    # Các nút điều chỉnh độ sáng
        self.btn_brightness = Button(self.control_frame, text="Chỉnh độ sáng", command=self.apply_brightness, relief="raised", font=("Helvetica", 12, "bold"), bg="#FFC107", fg="black")
        self.btn_brightness.grid(row=0, column=1, padx=10, pady=5)

        self.brightness_slider = Scale(self.control_frame, from_=0, to=100, orient=HORIZONTAL, label="Độ sáng", relief="sunken", sliderlength=20)
        self.brightness_slider.set(50)
        self.brightness_slider.grid(row=0, column=2, padx=10, pady=5)

        # Các nút điều chỉnh độ tương phản
        self.btn_contrast = Button(self.control_frame, text="Chỉnh độ tương phản", command=self.apply_contrast, relief="raised", font=("Helvetica", 12, "bold"), bg="#FFC107", fg="black")
        self.btn_contrast.grid(row=1, column=4, padx=10, pady=5)

        self.contrast_slider = Scale(self.control_frame, from_=0.1, to=2.0, orient=HORIZONTAL, resolution=0.1, label="Độ tương phản", relief="sunken", sliderlength=20)
        self.contrast_slider.set(1.0)
        self.contrast_slider.grid(row=1, column=5, padx=10, pady=5)

        # Các nút bộ lọc màu
        self.btn_sepia = Button(self.control_frame, text="Sepia", command=lambda: self.apply_color_filter('sepia'), relief="raised", font=("Helvetica", 12, "bold"), bg="#8E44AD", fg="black")
        self.btn_sepia.grid(row=1, column=0, padx=10, pady=5)

        self.btn_bw = Button(self.control_frame, text="Nền đen trắng", command=lambda: self.apply_color_filter('bw'), relief="raised", font=("Helvetica", 12, "bold"), bg="#8E44AD", fg="black")
        self.btn_bw.grid(row=1, column=1, padx=10, pady=5)

        # Nút cắt và thay đổi kích thước ảnh
        self.btn_crop_resize = Button(self.control_frame, text="Cắt & Resize", command=self.apply_crop_resize, relief="raised", font=("Helvetica", 12, "bold"), bg="#3498DB", fg="black")
        self.btn_crop_resize.grid(row=1, column=2, padx=10, pady=5)

        # Nút hoàn tác
        self.btn_undo = Button(self.control_frame, text="Hoàn tác", command=self.undo, relief="raised", font=("Helvetica", 12, "bold"), bg="#F39C12", fg="black")
        self.btn_undo.grid(row=1, column=3, padx=10, pady=5)
        
        # Nút reset
        self.btn_reset = Button(self.control_frame, text="Reset", command=self.reset_image, relief="raised", font=("Helvetica", 12, "bold"), bg="#F39C12", fg="black")
        self.btn_reset.grid(row=1, column=6, padx=10, pady=5)

        # Nút lưu ảnh
        self.btn_save = Button(self.control_frame, text="Lưu ảnh", command=self.save_image, relief="raised", font=("Helvetica", 12, "bold"), bg="#27AE60", fg="black")
        self.btn_save.grid(row=0, column=6, padx=10, pady=5)

        # Nút hiển thị biểu đồ màu cục bộ
        self.btn_local_histogram = Button(self.control_frame, text="Biểu đồ màu cục bộ", command=self.display_local_color_histogram, relief="raised", font=("Helvetica", 12, "bold"), bg="#9B59B6", fg="black")
        self.btn_local_histogram.grid(row=1, column=0, padx=10, pady=5)

        # Thêm nút chuyển sang giao diện Bộ lọc Cá Nhân
        self.btn_custom_filter = Button(self.control_frame, text="Bộ lọc cá nhân", command=self.show_custom_filter, relief="raised", font=("Helvetica", 12, "bold"), bg="#3498DB", fg="black")
        self.btn_custom_filter.grid(row=0, column=4, padx=10, pady=5)

        # Nút "Chọn bộ lọc"
        self.btn_select_filter = Button(self.control_frame, text="Chọn bộ lọc", command=self.select_filter, relief="raised", font=("Helvetica", 12, "bold"), bg="#3498DB", fg="black")
        self.btn_select_filter.grid(row=0, column=3, padx=10, pady=5)

        # Thêm nút "Xóa phông"
        self.btn_remove_background = Button(self.control_frame, text="Xóa phông", command=self.remove_background, relief="raised", font=("Helvetica", 12, "bold"), bg="#FF6347", fg="black")
        self.btn_remove_background.grid(row=0, column=5, padx=10, pady=5)

        self.image = None
        self.display_image = None
        self.history = []  # Lưu lại lịch sử ảnh để hoàn tác


    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:  # Kiểm tra nếu file_path không rỗng (người dùng chọn file)
           self.image = cv2.imread(file_path)
           self.history = [self.image.copy()]  # Lưu ảnh gốc vào lịch sử
           self.display_image_on_canvas()
        else:
            print("Không có file nào được chọn.")

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
        
    # Bộ lọc Luminous: Tăng cường độ sáng và làm sáng da
    def apply_luminous_filter(image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v = cv2.add(v, 50)  # Tăng độ sáng
        v = np.clip(v, 0, 255)
        final_hsv = cv2.merge((h, s, v))
        luminous_image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        return luminous_image

    # Bộ lọc Glowing: Tạo hiệu ứng phát sáng
    def apply_glowing_filter(image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v = cv2.add(v, 100)  # Tăng độ sáng lên mạnh mẽ
        s = cv2.multiply(s, 1.2)  # Tăng cường độ bão hòa màu
        v = np.clip(v, 0, 255)
        s = np.clip(s, 0, 255)
        final_hsv = cv2.merge((h, s, v))
        glowing_image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        return glowing_image

    # Bộ lọc Vintage: Tạo hiệu ứng cổ điển với tông màu ấm
    def apply_vintage_filter(image):
        kernel = np.array([[0.393, 0.769, 0.189],
                       [0.349, 0.686, 0.168],
                       [0.272, 0.534, 0.131]])
        vintage_image = cv2.transform(image, kernel)
        vintage_image = np.clip(vintage_image, 0, 255)
        return vintage_image

    # Bộ lọc Neon: Tạo hiệu ứng sáng neon
    def apply_neon_filter(image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        s = cv2.multiply(s, 1.5)  # Tăng độ bão hòa mạnh mẽ
        v = cv2.add(v, 50)  # Tăng độ sáng mạnh mẽ
        s = np.clip(s, 0, 255)
        v = np.clip(v, 0, 255)
        final_hsv = cv2.merge((h, s, v))    
        neon_image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        return neon_image
     # Hàm xử lý xóa phông
    def remove_background(self):
        if self.image is not None:
            self.image = remove_background(self.image)
            self.history.append(self.image.copy())  # Lưu lại lịch sử ảnh
            self.display_image_on_canvas()

    def display_image_on_canvas(self):
        if self.image is not None:
            image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            image_pil = Image.fromarray(image_rgb)
            self.display_image = ImageTk.PhotoImage(image_pil)
            self.canvas.create_image(400, 300, image=self.display_image, anchor="center")

    def undo(self):
        if len(self.history) > 1:
            self.history.pop()  # Loại bỏ ảnh hiện tại khỏi lịch sử
            self.image = self.history[-1]  # Quay lại ảnh trước đó
            self.display_image_on_canvas()
    
    def reset_image(self):
        if len(self.history) > 0:
            # Khôi phục ảnh gốc từ lịch sử
            self.image = self.history[0]  # Lấy ảnh gốc
            self.display_image_on_canvas()
 

    def display_image_on_canvas(self):
        if self.image is not None:
            image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            image_pil = Image.fromarray(image_rgb)
            self.display_image = ImageTk.PhotoImage(image_pil)
            self.canvas.create_image(400, 300, image=self.display_image, anchor="center")

    def display_local_color_histogram(self):
        if self.image is not None:
            x, y, width, height = 50, 50, 150, 150  # Vùng bạn muốn tính toán biểu đồ màu
            show_local_color_histogram(self.image, x, y, width, height)
    def select_filter(self):
        # Cửa sổ chọn bộ lọc
        filter_window = Toplevel(self.root)
        filter_window.title("Chọn bộ lọc")

        def apply_selected_filter(selected_filter):
            if selected_filter == "Luminous":
                self.image = apply_luminous_filter(self.image)
            elif selected_filter == "Glowing":
                self.image = apply_glowing_filter(self.image)
            elif selected_filter == "Vintage":
                self.image = apply_vintage_filter(self.image)
            elif selected_filter == "Neon":
                self.image = apply_neon_filter(self.image)
            self.display_image_on_canvas()  # Gọi phương thức đúng để hiển thị ảnh
            filter_window.destroy()

        # Thêm các nút lựa chọn bộ lọc
        filters = ["Luminous", "Glowing", "Vintage", "Neon"]
        for i, filter_name in enumerate(filters):
            Button(filter_window, text=filter_name, command=lambda filter_name=filter_name: apply_selected_filter(filter_name)).grid(row=i, column=0, padx=10, pady=5)

    def show_custom_filter(self):
        CustomFilterWindow(self.root, self)
    
class CustomFilterWindow:
    def __init__(self, root, parent_app):
        self.root = root
        self.parent_app = parent_app
        self.top = Toplevel(root)
        self.top.title("Bộ lọc cá nhân")

        self.label = Label(self.top, text="Chỉnh sửa bộ lọc cá nhân", font=("Arial", 16))
        self.label.pack(pady=10)

        # Các thanh trượt cho bộ lọc cá nhân
        self.hue_slider = Scale(self.top, from_=0, to=360, orient=HORIZONTAL, label="Hue (Màu sắc)", relief="sunken", sliderlength=20)
        self.hue_slider.set(0)
        self.hue_slider.pack(padx=10, pady=5)

        self.saturation_slider = Scale(self.top, from_=0, to=100, orient=HORIZONTAL, label="Saturation (Bão hòa)", relief="sunken", sliderlength=20)
        self.saturation_slider.set(100)
        self.saturation_slider.pack(padx=10, pady=5)

        self.brightness_slider = Scale(self.top, from_=0, to=100, orient=HORIZONTAL, label="Brightness (Độ sáng)", relief="sunken", sliderlength=20)
        self.brightness_slider.set(50)
        self.brightness_slider.pack(padx=10, pady=5)

        self.apply_button = Button(self.top, text="Áp dụng bộ lọc", command=self.apply_filter, relief="raised", font=("Arial", 12, "bold"), bg="#3498DB", fg="white")
        self.apply_button.pack(pady=20)

    def apply_filter(self):
        hue = self.hue_slider.get()
        saturation = self.saturation_slider.get()
        brightness = self.brightness_slider.get()

        # Tạo bộ lọc tùy chỉnh
        hsv = cv2.cvtColor(self.parent_app.image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        h = cv2.add(h, hue - 0)  # Điều chỉnh Hue
        s = cv2.multiply(s, saturation / 100.0)  # Điều chỉnh Saturation
        v = cv2.add(v, brightness - 50)  # Điều chỉnh Brightness
        v = np.clip(v, 0, 255)

        hsv = cv2.merge((h, s, v))
        self.parent_app.image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        self.parent_app.history.append(self.parent_app.image.copy())  # Lưu lại lịch sử ảnh
        self.parent_app.display_image_on_canvas()
        self.top.destroy()

if __name__ == "__main__":
    root = Tk()
    app = PhotoEditor(root)
    root.mainloop()