from picamera2 import Picamera2

picam2 = Picamera2()

def take_photo(save_as: str | None = "camera.png") -> None:
    picam2.start_and_capture_file("camera.png")


