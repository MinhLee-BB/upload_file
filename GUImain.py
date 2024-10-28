from seabreeze.spectrometers import Spectrometer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
import numpy as np
import time

# Khởi tạo giao diện Tkinter
root = tk.Tk()
root.title("Mô phỏng đo Raman lệch tâm")
root.attributes('-fullscreen', False)

# Hàm thoát chế độ toàn màn hình
def exit_fullscreen(event=None):
    root.attributes('-fullscreen', False)

# Kích thước màn hình
spectral_frame_width = int(root.winfo_screenwidth() * 0.7)
spectral_frame_height = int(root.winfo_screenheight() * 0.9)

# Khung chính của giao diện
Spectral_frame = tk.Frame(root, width=spectral_frame_width, height=spectral_frame_height, bg="lightblue")
Spectral_frame.pack(side="left", fill="both", expand=True)

# Khởi tạo quang phổ kế
spec = Spectrometer.from_first_available()

# Biến toàn cục để lưu dữ liệu quang phổ và ID của sự kiện after
spectrum_data = None
wavelengths_data = None
after_id = None  # Biến lưu ID sự kiện after
update_interval = 1000  # Thời gian đo mặc định (ms)
last_measure_time = 0  # Thời gian lần đo quang phổ gần nhất

# Tạo một Figure và Axes cho biểu đồ
fig, ax = plt.subplots(figsize=(8, 6))
line, = ax.plot([], [], label='Quang phổ từ USB2000', color='blue')  # Tạo một đường cho biểu đồ
ax.set_title("Quang phổ từ USB2000")
ax.set_xlabel("Bước sóng (nm)")
ax.set_ylabel("Cường độ ánh sáng")
ax.grid(True)
ax.legend()

# Cố định trục Y với giá trị tối thiểu và tối đa ban đầu
ax.set_ylim([0, 2000])  # Đặt giới hạn trục Y từ 0 đến 2000

# Hàm để vẽ biểu đồ quang phổ
def draw_spectrum():
    global canvas, spectrum_data, wavelengths_data, after_id, last_measure_time

    current_time = time.time() * 1000  # Lấy thời gian hiện tại (ms)

    # Kiểm tra xem đã đến lúc đo lại dữ liệu từ quang phổ kế chưa
    if current_time - last_measure_time >= update_interval:
        # Lấy dữ liệu từ quang phổ kế
        wavelengths = spec.wavelengths()  # Lấy bước sóng
        spectrum = spec.intensities()     # Đọc cường độ phổ

        # Cập nhật dữ liệu quang phổ
        wavelengths_data = wavelengths
        spectrum_data = spectrum

        # Cập nhật đường biểu đồ
        line.set_data(wavelengths, spectrum)

        # Điều chỉnh giới hạn trục X
        ax.set_xlim([min(wavelengths), max(wavelengths)])

        # Cập nhật thời gian đo gần nhất
        last_measure_time = current_time

    # Vẽ lại biểu đồ mỗi khung hình (đảm bảo ít nhất 60 FPS)
    canvas.draw()

    # Gọi lại hàm này sau 16 ms (~60 FPS)
    after_id = root.after(16, draw_spectrum)

# Khung nhập liệu
input_frame = tk.Frame(root)
input_frame.pack(side="right", fill="y", padx=20)

# Ô nhập liệu cho thời gian cập nhật
tk.Label(input_frame, text="Thời gian đo (ms):").pack(pady=10)
time_entry = tk.Entry(input_frame)
time_entry.insert(0, "1000")  # Giá trị mặc định
time_entry.pack(pady=5)

# Nút cập nhật thời gian cập nhật
def update_update_interval():
    global update_interval
    try:
        update_interval = max(16, int(time_entry.get()))  # Lấy giá trị từ ô nhập liệu và đảm bảo không nhỏ hơn 16 ms
    except ValueError:
        pass  # Không làm gì nếu không hợp lệ

update_time_btn = tk.Button(input_frame, text="Cập nhật thời gian đo", command=update_update_interval)
update_time_btn.pack(pady=10)

# Nhúng biểu đồ vào Tkinter
canvas = FigureCanvasTkAgg(fig, master=Spectral_frame)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Thêm thanh công cụ có chức năng zoom
toolbar_frame = tk.Frame(master=Spectral_frame)
toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
toolbar.update()

# Hàm điều chỉnh biểu đồ để lấp đầy chiều cao của biểu đồ (trục Y) vào cửa sổ
def scale_graph_height_to_fill():
    # Lấy các giá trị hiện tại của trục Y
    ymin, ymax = ax.get_ylim()

    # Lấy cường độ lớn nhất của phổ hiện tại để điều chỉnh giới hạn Y
    if spectrum_data is not None:
        ymax = max(spectrum_data)
        ymin = min(spectrum_data)

    # Điều chỉnh giới hạn trục Y để khớp với cường độ phổ
    ax.set_ylim([ymin, ymax])

    # Vẽ lại biểu đồ
    canvas.draw()

# Hàm điều chỉnh biểu đồ để lấp đầy toàn bộ trục X và Y vào khung biểu đồ
def scale_graph_to_fill():
    # Điều chỉnh cả trục X và trục Y dựa trên dữ liệu hiện tại
    if spectrum_data is not None and wavelengths_data is not None:
        ax.set_xlim([min(wavelengths_data), max(wavelengths_data)])
        ax.set_ylim([min(spectrum_data), max(spectrum_data)])

    # Vẽ lại biểu đồ
    canvas.draw()

# Nút để lấp đầy biểu đồ vào khung cửa sổ
scale_graph_btn = tk.Button(input_frame, text="Scale Graph to Fill Window", command=scale_graph_to_fill)
scale_graph_btn.pack(pady=10)

# Nút để chỉ lấp đầy chiều cao biểu đồ (trục Y) vào khung cửa sổ
scale_graph_height_btn = tk.Button(input_frame, text="Scale Graph Height to Fill Window", command=scale_graph_height_to_fill)
scale_graph_height_btn.pack(pady=10)

# Gọi hàm vẽ biểu đồ quang phổ lần đầu
draw_spectrum()

# Gán phím Escape để thoát chế độ toàn màn hình
root.bind("<Escape>", exit_fullscreen)

# Đảm bảo đóng kết nối khi thoát
def on_closing():
    global after_id
    if after_id is not None:
        root.after_cancel(after_id)  # Hủy sự kiện after trước khi thoát
    spec.close()  # Đóng kết nối quang phổ kế
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Chạy chương trình
root.mainloop()
