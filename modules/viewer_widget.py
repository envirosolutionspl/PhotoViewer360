import math
import os

from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_BLEND,
    GL_LINEAR,
    GL_LINES,
    GL_MODELVIEW,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_PROJECTION,
    GL_RGBA,
    GL_RGB,
    GL_SRC_ALPHA,
    GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TRIANGLES,
    GL_UNSIGNED_BYTE,
    glBegin,
    glBindTexture,
    glBlendFunc,
    glClear,
    glClearColor,
    glColor3f,
    glVertex3fv,
    glColor3fv,
    glEnable,
    glDisable,
    glEnd,
    glGenerateMipmap,
    glGenTextures,
    glLineWidth,
    glLoadIdentity,
    glMatrixMode,
    glPopMatrix,
    glPushMatrix,
    glRotatef,
    glTexImage2D,
    glTexParameteri,
    glTranslatef,
    glVertex2f,
    glViewport,
    glRasterPos,
    glDrawPixels
)

from OpenGL.GLU import (
    gluNewQuadric,
    gluOrtho2D,
    gluPerspective,
    gluQuadricTexture,
    gluSphere,
)
from PIL import Image
from PIL import ImageFont, ImageDraw
from qgis.PyQt import QtCore

if int(QtCore.qVersion().split('.')[0]) > 5:
    from PyQt6.QtGui import QSurfaceFormat
    from PyQt6.QtOpenGLWidgets import QOpenGLWidget
else:
    from PyQt5.QtGui import QSurfaceFormat
    from PyQt5.QtWidgets import QOpenGLWidget

from ..utils import MessageUtils

from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsUnitTypes,
    QgsVectorLayer
)

from .. import plugin_dir

class ViewerWidget(QOpenGLWidget):
    """ QWidget Renderujący Widok Perspektywiczny na podstawie zdjęcia EquiProstokątnego """

    # Obsługa Qt5 i Qt6
    _QtCore_Qt_MouseButton_LeftButton = None
    _QtCore_Qt_CursorShape_OpenHandCursor = None
    _QtCore_Qt_CursorShape_ClosedHandCursor = None
    _QtCore_Qt_CursorShape_WaitCursor = None

    _QtCore_Qt_QSurfaceFormat_OpenGLContextProfile_CompatibilityProfile = None

    mouse_x = 0
    mouse_y = 0

    def _obslugaQt5iQt6(self):
        """ Obsługa Qt5 i Qt6 - inicjacja zmiennych """
        if hasattr(QtCore.Qt,"MouseButton"):
            self._QtCore_Qt_MouseButton_LeftButton = QtCore.Qt.MouseButton.LeftButton # Qt6
        else:
            self._QtCore_Qt_MouseButton_LeftButton = QtCore.Qt.LeftButton #Qt5

        if hasattr(QtCore.Qt,"CursorShape"):
            self._QtCore_Qt_CursorShape_OpenHandCursor = QtCore.Qt.CursorShape.OpenHandCursor # Qt6
        else:
            self._QtCore_Qt_CursorShape_OpenHandCursor = QtCore.Qt.OpenHandCursor #Qt5    

        if hasattr(QtCore.Qt,"CursorShape"):
            self._QtCore_Qt_CursorShape_ClosedHandCursor = QtCore.Qt.CursorShape.ClosedHandCursor # Qt6
        else:
            self._QtCore_Qt_CursorShape_ClosedHandCursor = QtCore.Qt.ClosedHandCursor #Qt5  

        if hasattr(QtCore.Qt,"CursorShape"):
            self._QtCore_Qt_CursorShape_WaitCursor = QtCore.Qt.CursorShape.WaitCursor # Qt6
        else:
            self._QtCore_Qt_CursorShape_WaitCursor = QtCore.Qt.WaitCursor #Qt5  

        if hasattr(QSurfaceFormat, "OpenGLContextProfile"):
            self._QtCore_Qt_QSurfaceFormat_OpenGLContextProfile_CompatibilityProfile = \
                QSurfaceFormat.OpenGLContextProfile.CompatibilityProfile # Qt6
        else:
            self._QtCore_Qt_QSurfaceFormat_OpenGLContextProfile_CompatibilityProfile = \
                QSurfaceFormat.CompatibilityProfile # Qt5
            

    def __init__(
        self, parent, iface,
        direction, angle_degrees, x, y,
        nazwa_pliku, data_wykonania="", nr_drogi="", nazwa_ulicy="NULL", numer_odcinka="", kilometraz=""
        ):
        """
        Widget wyświetlający podgląd equiprostokątnego zdjęcie w formie podglądu 360

        """
        
        # Obsługa Qt5 i Qt6
        self._obslugaQt5iQt6()

        format = QSurfaceFormat()
        format.setProfile(self._QtCore_Qt_QSurfaceFormat_OpenGLContextProfile_CompatibilityProfile)
        QSurfaceFormat.setDefaultFormat(format)
        
        super().__init__(parent)
        self.showDescription = True
        self.iface = iface
        self.x = x
        self.y = y
        self.prev_dx = 0
        self.prev_dy = 0
        self.direction = direction
        self.angle_degrees = angle_degrees
        self.parent = parent

        self.nazwa_pliku = nazwa_pliku
        self.data_wykonania = data_wykonania
        self.nr_drogi = nr_drogi
        self.nazwa_ulicy = nazwa_ulicy
        self.numer_odcinka = numer_odcinka
        self.kilometraz = kilometraz

        self.image_description_data = None
        self.new_image_description_data = None
        
        self.is_widget_loaded = False
        self.is_texture_loaded = False
        try:
            self.image = Image.open(self.nazwa_pliku)
        except Exception:
            iface.messageBar().pushMessage(
                "Unable to load the image, please verify image's source",
                level=Qgis.Info,
            )
        self.image_width, self.image_height = self.image.size
        self.yaw = 90 - (direction - ((450 - angle_degrees) % 360))
        self.pitch = 0
        self.sensitivity = 1
        self.fov = 60
        self.moving = False
        self.direction = angle_degrees

        # system hotspotow
        self.coordinates = None
        self.vertices_group = None
        self.faces_group = None
        
    def loadTexture(self, nazwa_pliku):
        """
        Wczytuje zdjęcie do pamięci OpenGL lub je odświeża. Nazwa zostaje zapamiętana w klasie ViewerWidget.

        """
        self.is_texture_loaded = False
        self.nazwa_pliku = nazwa_pliku
        try:
            # Wczytywanie zdjęcia equiprostokątnego do pamięci
            image = Image.open(nazwa_pliku)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            image_data = image.tobytes("raw", "RGBX", 0, -1)

            if not hasattr(self, "texture_id"): # chyba jedna instancja tekstury wystarczy
                self.texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RGBA,
                image.width,
                image.height,
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                image_data,
            )
            glGenerateMipmap(GL_TEXTURE_2D)
            self.is_texture_loaded = True

        except Exception as e:
            # dodać komunikat dla użytkownika
            # print(f"Texture loading error: {e}")
            pass

    def initializeGL(self):
        """
        Funkcja inicjująca ustawienia OpenGL.

        """
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_TEXTURE_2D)
        self.loadTexture(self.nazwa_pliku)
        self.setupProjection()
        self.setDataAboutPhoto(self.nazwa_pliku, self.data_wykonania, self.nr_drogi, self.nazwa_ulicy, self.numer_odcinka, self.kilometraz)
        self.image_description_data = self.new_image_description_data

    def setupProjection(self):
        """
        Funkcja ustawiająca projekcję perspektywiczną.

        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90, self.width() / self.height(), 0.1, 1000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        """
        Obsługa wywołania OpenGL odpowiedzialnego za rysowanie.

        """
        glLoadIdentity()
        gluPerspective(self.fov, self.width() / self.height(), 0.1, 1000)
        self.renderScene()
        self.parent.updateOrientation(self.yaw-90.0)

        # zmienna zapobiegająca ładowaniu obiektów do OpenGL przed końcem inicjacji
        self.is_widget_loaded = True

    def renderScene(self):
        """
        Rysowanie sceny
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        self.applyRotation()    
        self.drawSphere()
        self.drawHotSpots() # obniża hotspoty
        glPopMatrix()
        if self.showDescription:
            self.drawDescriptionBalloom()
            pass

    def applyRotation(self):
        glRotatef(self.pitch, 1, 0, 0)
        glRotatef(self.yaw, 0, 1, 0)
        glRotatef(90, 1, 0, 0)
        glRotatef(90, 0, 0, 1)

    def drawSphere(self):
        if hasattr(self, "texture_id") and self.is_texture_loaded:
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
        else:
            print("No texture loaded, drawing without texture.")
        sphere = gluNewQuadric()
        gluQuadricTexture(sphere, True)
        gluSphere(sphere, 10, 100, 100)

    def drawDescriptionBalloom(self):
        """
        Rysuje dymek z opisem na oknie OpenGL
        """
        if self.image_description_data is not None:
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            gluOrtho2D(0, self.width(), self.height(), 0)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()       

            # Rysowanie dymka z informacjami
            glColor3fv([1, 1, 1]) 
            glRasterPos(0, 260) # lub glRasterPos(0, 207) - na niektórych konfiguracjach było przesunięcie
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glDrawPixels(300, 260, GL_RGBA, GL_UNSIGNED_BYTE, self.image_description_data)
            glDisable(GL_BLEND)

            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            # glMatrixMode(GL_MODELVIEW)
            # glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(self.fov, self.width() / self.height(), 0.1, 1000)

            return True
        else:
            return False

    def updateViewerWigdet(self, direction, angle_degrees, x, y, nazwa_pliku, data_wykonania="", nr_drogi="", nazwa_ulicy="NULL", numer_odcinka="", kilometraz=""):
        if self.is_widget_loaded:
            self.direction = direction
            self.angle_degrees = angle_degrees
            self.x = x
            self.y = y
            self.loadTexture(nazwa_pliku)
            self.setDataAboutPhoto(nazwa_pliku, data_wykonania, nr_drogi, nazwa_ulicy, numer_odcinka, kilometraz)
            self.image_description_data = self.new_image_description_data
            self.update()
            return True
        else:
            # TODO Komunikat
            return False    
        
    def updateViewerWigdet(self, direction, angle_degrees, x, y):
        if self.is_widget_loaded:
            self.direction = direction
            self.angle_degrees = angle_degrees
            self.x = x
            self.y = y
            self.loadTexture(self.nazwa_pliku)
            self.image_description_data = self.new_image_description_data
            self.update()
            return True
        else:
            # TODO Komunikat
            return False 

    def setDataAboutPhoto(self, nazwa_pliku, data_wykonania, nr_drogi, nazwa_ulicy, numer_odcinka, kilometraz):
        """
        Wprowadzanie danych opisowych zdjęcia do Widgetu
        """
        self.data_wykonania = data_wykonania
        self.nr_drogi = nr_drogi
        self.nazwa_ulicy = nazwa_ulicy
        self.numer_odcinka = numer_odcinka
        self.kilometraz = kilometraz
        self.nazwa_pliku = nazwa_pliku

        try:
            image = Image.open(os.path.join(plugin_dir, "images", "desc_balloon.png"))
        except Exception:
            # TODO Komunikat
            return False
        try:
            font_regular = ImageFont.truetype(os.path.join(plugin_dir, "fonts", "Roboto_SemiCondensed-Regular.ttf"), 15)
            font_bold = ImageFont.truetype(os.path.join(plugin_dir, "fonts", "Roboto_SemiCondensed-Bold.ttf"), 15)
        except Exception:
            # TODO Komunikat
            return False

        # Generowanie opisu na dymku
        draw = ImageDraw.Draw(image)
        draw.text((10, 84), "Numer drogi:", fill=(0, 0, 0), font=font_bold)
        draw.text((10, 100), nr_drogi, fill=(0, 0, 0), font=font_regular)
        if nazwa_ulicy != "NULL":
            draw.text((10, 116), "Nazwa ulicy:", fill=(0, 0, 0), font=font_bold)
            draw.text((10, 132), nazwa_ulicy, fill=(0, 0, 0), font=font_regular)
            draw.text((10, 148), "Numer odcinka:", fill=(0, 0, 0), font=font_bold)
            draw.text((10, 164), numer_odcinka, fill=(0, 0, 0), font=font_regular)
            draw.text((10, 180), "Kilometraż:", fill=(0, 0, 0), font=font_bold)
            draw.text((10, 196), kilometraz, fill=(0, 0, 0), font=font_regular)
            draw.text((10, 212), "Data:", fill=(0, 0, 0), font=font_bold)
            draw.text((10, 228), data_wykonania, fill=(0, 0, 0), font=font_regular)

        self.new_image_description_data = image.tobytes("raw", "RGBA", 0, -1)
        return True

    def setHotSpots(self, coordinates):
        """
        Ustawienie hotSpotow według podanej listy
        """
        self.coordinates = coordinates            

        if self.coordinates is not None:
            # wczytywanie obiektów hotspotów do pamięci
            self.vertices_group = []
            self.faces_group = []
            scale = 0.104 # skalowanie dystansu od obserwatora dla widoku OpenGL
            for hotspot in self.coordinates:
                if hotspot['distance'] < 0.01:
                    continue
                vertices = []
                faces = []
                with open(os.path.join(plugin_dir, "images", "hotspot.obj"), 'r') as f:
                    for line in f:
                        if line.startswith('v '):
                            ver = list(map(float, line.strip().split()[1:]))
                            # wyliczanie przesunięcia wierchołków na podstawie kąta i dystansu hotspota
                            # x = r*cos(kat_w_radianach)
                            # y = r*sin(kat_w_radianach), r= scale*distance, kat_w_radianach= azymut_obliczony
                            ver[0] = ver[0]+scale*hotspot['distance']*math.cos(hotspot['azymut_obliczony'])
                            ver[1] = ver[1]+scale*hotspot['distance']*math.sin(hotspot['azymut_obliczony'])
                            ver[2] = ver[2]+0.3
                            vertices.append(ver)
                        elif line.startswith('f '):
                            face = [int(val.split('/')[0]) - 1 for val in line.strip().split()[1:]]
                            faces.append(face)
                self.vertices_group.append(vertices)
                self.faces_group.append(faces)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.width() / self.height(), 0.1, 1000)

    def mousePressEvent(self, event):
        if event.button() == self._QtCore_Qt_MouseButton_LeftButton:
            self.moving = False
            self.mouse_x, self.mouse_y = event.pos().x(), event.pos().y()
            self.setCursor(self._QtCore_Qt_CursorShape_ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        if not self.moving:
            # TODO Dodać obsługę kliknięcia w hotSpoty
            self.update()
            
        if event.button() == self._QtCore_Qt_MouseButton_LeftButton:
            self.setCursor(self._QtCore_Qt_CursorShape_OpenHandCursor)


    def mouseMoveEvent(self, event):
        self.moving = True

        # obracanie okna
        dx = event.pos().x() - self.mouse_x
        dy = event.pos().y() - self.mouse_y
        dx *= 0.1
        dy *= 0.1
        self.yaw -= dx * self.sensitivity
        self.pitch -= dy * self.sensitivity
        self.pitch = min(max(self.pitch, -90), 90)
        self.mouse_x, self.mouse_y = event.pos().x(), event.pos().y()
        self.direction += dx
        self.update()

        self.prev_dx = dx
        self.prev_dy = dy

    def drawHotSpots(self):
        if self.vertices_group is not None and self.faces_group is not None:
            for i in range(0, len(self.vertices_group)):
                
                if self.vertices_group[i] is not None and self.faces_group[i] is not None:
                    glBegin(GL_TRIANGLES)
                    for face in self.faces_group[i]:
                        for vertex in face:
                            glColor3fv([0.7, 0.7, 0.7]) 
                            glVertex3fv([self.vertices_group[i][vertex][0], self.vertices_group[i][vertex][1], self.vertices_group[i][vertex][2]])
                    glColor3fv([1, 1, 1]) 
                    glEnd()        

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.fov -= delta * 0.1
        self.fov = max(30, min(self.fov, 90))
        self.sensitivity = self.fov / 60
        self.update()

    def recalculate_coordinates(self, x, y, angle, distance):
        angle_rad = math.radians(angle)
        point = QgsPointXY(x, y)
        if QgsProject.instance().crs().mapUnits() == QgsUnitTypes.DistanceDegrees:
            src_crs = QgsCoordinateReferenceSystem("EPSG:4326")
            dst_crs = QgsCoordinateReferenceSystem("EPSG:3857")
            transform = QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())
            untransform = QgsCoordinateTransform(
                dst_crs, src_crs, QgsProject.instance()
            )
            point = transform.transform(point)

        x_new = point.x() + (distance * math.cos(angle_rad))
        y_new = point.y() + (distance * math.sin(angle_rad))
        if QgsProject.instance().crs().mapUnits() == QgsUnitTypes.DistanceDegrees:
            point = QgsPointXY(x_new, y_new)
            point = untransform.transform(point)
            x_new = point.x()
            y_new = point.y()
        return x_new, y_new

