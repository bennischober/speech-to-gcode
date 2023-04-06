import cv2

# Lade das Bild
img = cv2.imread("elefant2.jpeg")

# Wandle das Bild in Graustufen um
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Rauschen eliminieren
blurred = cv2.GaussianBlur(gray, (3, 3), 0)

# Kanten mit Canny-Detektor finden
edges = cv2.Canny(blurred, 100, 200)

# Vergrößere die Kantenbreite auf mindestens 8 Pixel
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
dilated = cv2.dilate(edges, kernel)

# Zeige das Ergebnis
cv2.imshow("Kanten erkannt", dilated)
cv2.waitKey(0)