import cv2

# Chỉ số 0 thường là camera tích hợp/mặc định. 
# Nếu dùng camera USB rời, hãy thử đổi thành 1, 2 nếu màn hình không hiện đúng cam.
camera_index = 0

cap = cv2.VideoCapture(camera_index)

# Kiểm tra xem có kết nối được với camera không
if not cap.isOpened():
    print(f"Lỗi: Không thể mở camera ở cổng {camera_index}!")
    print("Gợi ý: Thử đổi camera_index = 1 hoặc kiểm tra lại cổng cắm USB.")
    exit()

print("Camera đã mở thành công. Nhấn phím 'q' trên cửa sổ video để thoát.")

while True:
    ret, frame = cap.read()
    
    # Nếu không đọc được khung hình
    if not ret:
        print("Lỗi: Không nhận được khung hình từ camera.")
        break

    # Hiển thị luồng video
    cv2.imshow("Test USB Camera", frame)

    # Chờ 1ms và kiểm tra nếu bấm phím 'q' thì dừng lại
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng camera và đóng các cửa sổ
cap.release()
cv2.destroyAllWindows()