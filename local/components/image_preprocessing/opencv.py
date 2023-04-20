import cv2

# Bild laden
img = cv2.imread("bild.png")

# Graustufenbild
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Rauschen eliminieren
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# Canny-Kanten-Detektor
edges = cv2.Canny(blurred, 100, 200)

# Kantenbreite (4 Pixel)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
dilated = cv2.dilate(edges, kernel)

# Ausgabe
cv2.imshow("Kanten erkannt", dilated)
cv2.waitKey(0)