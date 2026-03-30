import math
import os

from OpenGL.GL import *
from OpenGL.GLU import (
    gluNewQuadric,
    gluOrtho2D,
    gluPerspective,
    gluQuadricTexture,
    gluSphere,
)

from PIL import Image, ImageFont, ImageDraw
from qgis.PyQt import QtCore
from qgis.PyQt.QtGui import QSurfaceFormat

if int(QtCore.qVersion().split(".")[0]) > 5:
    try:
        from qgis.PyQt.QtOpenGLWidgets import QOpenGLWidget
    except ModuleNotFoundError:
        from PyQt6.QtOpenGLWidgets import QOpenGLWidget
else:
    from qgis.PyQt.QtWidgets import QOpenGLWidget

from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsPointXY,
    QgsProject,
    QgsUnitTypes,
)

from ..utils import MessageUtils
from .. import plugin_dir

class ViewerWidget(QOpenGLWidget):
    """ QWidget Renderujący Widok Perspektywiczny na podstawie zdjęcia EquiProstokątnego """

    # Obsługa Qt5 i Qt6
    _QtCore_Qt_MouseButton_LeftButton = None
    _QtCore_Qt_CursorShape_OpenHandCursor = None
    _QtCore_Qt_CursorShape_ClosedHandCursor = None
    _QtCore_Qt_CursorShape_WaitCursor = None

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

    def __init__(
        self, parent, iface,
        direction,
        nazwa_pliku, data_wykonania="", nr_drogi="", nazwa_ulicy="NULL", numer_odcinka="", kilometraz=""
        ):
        """
        Widget wyświetlający podgląd equiprostokątnego zdjęcie w formie podglądu 360

        """
        
        # Obsługa Qt5 i Qt6
        self._obslugaQt5iQt6()

        format = QSurfaceFormat()
        format.setProfile(QSurfaceFormat.OpenGLContextProfile.CompatibilityProfile)
        # Qt5: QSurfaceFormat.ColorSpace enum; Qt6: setColorSpace(QColorSpace)
        if hasattr(QSurfaceFormat, "ColorSpace"):
            format.setColorSpace(QSurfaceFormat.ColorSpace.sRGBColorSpace)
        else:
            from qgis.PyQt.QtGui import QColorSpace

            if hasattr(QColorSpace, "sRgb"):
                format.setColorSpace(QColorSpace.sRgb())
            else:
                format.setColorSpace(QColorSpace(QColorSpace.NamedColorSpace.SRgb))
        QSurfaceFormat.setDefaultFormat(format)
        super().__init__(parent)
        self.show_description = True
        self.iface = iface
        self.prev_dx = 0
        self.prev_dy = 0
        self.direction = direction
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
        self.is_screen_shot_mode_activated = False
        self.is_texture_loaded = False

        try:
            self.image = Image.open(self.nazwa_pliku)
        except Exception:
            iface.messageBar().pushMessage(
                "Unable to load the image, please verify image's source",
                level=Qgis.Info,
            )
            
        self.yaw = direction
        self.pitch = 0
        self.sensitivity = 1
        self.fov = 60
        self.moving = False

        # system hotspotow
        self.coordinates = None
        self.obj_black_vertices = None
        self.obj_black_faces = None
        self.obj_white_vertices = None
        self.obj_white_faces = None
        self.obj_x = None
        self.obj_y = None
        self.hotspot_fid = None
        self.hot_spot_test = False
        self.hot_spot_last_rgb = 0
        self.viewport = []

        
    def loadTexture(self, nazwa_pliku):
        """
        Wczytuje zdjęcie do pamięci OpenGL lub je odświeża. Nazwa zostaje zapamiętana w klasie ViewerWidget.

        """
        self.is_texture_loaded = False
        self.nazwa_pliku = nazwa_pliku
        if os.path.exists(nazwa_pliku) is False:
            nazwa_pliku = os.path.join(plugin_dir, "images", "no_image.jpg")
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
                GL_TEXTURE_2D,  0, GL_RGBA,
                image.width, image.height,
                0, GL_RGBA, GL_UNSIGNED_BYTE,
                image_data,
            )
            glGenerateMipmap(GL_TEXTURE_2D)
            self.is_texture_loaded = True
        except FileNotFoundError:
            MessageUtils.pushLogCritical("Nie znaleziono pliku zdjęcia.")
        except Exception:
            MessageUtils.pushLogCritical("Błąd podczas wczytywania zdjęcia.")

    def loadHotspotObjects(self):
        """
        Wczytuje objekty OBJ do pamięci OpenGL.

        """
        self.obj_black_vertices = []
        self.obj_black_faces = []
        self.obj_white_vertices = []
        self.obj_white_faces = []

        try:
            with open(os.path.join(plugin_dir, "images", "hotspot_black.obj"), 'r') as f:
                for line in f:
                    if line.startswith('v '):
                        ver = list(map(float, line.strip().split()[1:]))
                        self.obj_black_vertices.append(ver)
                    elif line.startswith('f '):
                        face = [int(val.split('/')[0]) - 1 for val in line.strip().split()[1:]]
                        self.obj_black_faces.append(face)
        except FileNotFoundError:
            MessageUtils.pushLogWarning("Nie znaleziono pliku hotspot_black.obj")
            return False
        except Exception:
            MessageUtils.pushLogWarning("Błąd podczas odczytu pliku hotspot_black.obj")
            return False

        try:
            with open(os.path.join(plugin_dir, "images", "hotspot.obj"), 'r') as f:
                for line in f:
                    if line.startswith('v '):
                        ver = list(map(float, line.strip().split()[1:]))
                        self.obj_white_vertices.append(ver)
                    elif line.startswith('f '):
                        face = [int(val.split('/')[0]) - 1 for val in line.strip().split()[1:]]
                        self.obj_white_faces.append(face)
        except FileNotFoundError:
            MessageUtils.pushLogWarning("Nie znaleziono pliku hotspot.obj")
            return False
        except Exception:
            MessageUtils.pushLogWarning("Błąd podczas odczytu pliku hotspot.obj")
            return False

        return True

    def initializeGL(self):
        """
        Funkcja inicjująca ustawienia OpenGL.

        """
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_FRAMEBUFFER_SRGB)
        
        self.loadTexture(self.nazwa_pliku)
        self.loadHotspotObjects()
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
        self.viewport = glGetIntegerv(GL_VIEWPORT)

    def paintGL(self):
        """
        Obsługa wywołania OpenGL odpowiedzialnego za rysowanie.

        """
        glLoadIdentity()
        gluPerspective(self.fov, self.width() / self.height(), 0.1, 1000)
        self.renderScene()
        # wyzwalanie aktualizacji QgsRubberBand jeśli poprawnie wczytano zdjęcie
        if self.parent.is_current_image_exists:
            self.parent.updateOrientation(self.yaw-90.0)

        # zmienna zapobiegająca ładowaniu obiektów do OpenGL przed końcem inicjacji
        self.is_widget_loaded = True

    def renderScene(self):
        """
        Rysowanie sceny
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 3D: Rysowanie tła i ciemnych hotspotów
        glPushMatrix()
        self.applyRotation()    
        self.drawSphere()
        self.drawBlackHotSpots(self.hot_spot_test)
        glPopMatrix()

        # 2D: Testowanie hotspotów 
        glLoadIdentity()
        self.testHotSpots()

        # 3D: Rysowanie białych hotspotów 
        glLoadIdentity()
        gluPerspective(self.fov, self.width() / self.height(), 0.1, 1000)
        glPushMatrix()
        self.applyRotation()
        self.drawHotSpots()
        glPopMatrix()

        # 2D: Rysowanie opisu
        glLoadIdentity()
        if self.show_description:
            self.drawDescriptionBalloom()

        glLoadIdentity()

    def applyRotation(self):
        """
        Obracanie sceny z położenia wyjściowego do położenia zgodnego z aktualną pozycją obserwatora
        """
        glRotatef(self.pitch, 1, 0, 0)
        glRotatef(self.yaw, 0, 1, 0)
        glRotatef(90, 1, 0, 0)
        glRotatef(90, 0, 0, 1)

    def drawSphere(self):
        """
        Rysowanie sfery na podstawie equikwadratowego zdjęcia
        """
        glEnable(GL_TEXTURE_2D)
        if hasattr(self, "texture_id") and self.is_texture_loaded:
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
        sphere = gluNewQuadric()
        gluQuadricTexture(sphere, True)
        gluSphere(sphere, 15, 100, 100)
        glDisable(GL_TEXTURE_2D)

    def drawDescriptionBalloom(self):
        """
        Rysowanie dymka z opisem na oknie OpenGL
        """
        if self.image_description_data is not None:
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()

            gluOrtho2D(0, self.viewport[2], self.viewport[3], 0)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()    

            # aktualizacja danych o wymiarach viewport - przydaje się przy przerzucaniu okna między monitorami o różnym skalowaniu
            self.viewport = glGetIntegerv(GL_VIEWPORT)   

            # Rysowanie dymka z informacjami
            glColor3f(1, 1, 1) 
            glRasterPos(0, 260)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            if self.is_screen_shot_mode_activated:
                glDrawPixels(300, 260, GL_RGB, GL_UNSIGNED_BYTE, self.image_description_data)
            else:
                glDrawPixels(300, 260, GL_RGBA, GL_UNSIGNED_BYTE, self.image_description_data)
            glDisable(GL_BLEND)

            # finalizacja GL
            glColor3f(1, 1, 1) 
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            return True
        else:
            return False

    def drawBlackHotSpots(self, test_color=False):
        """
        Rysowanie ciemnych hot spotów w kolorze domyślnym lub do identyfikacji
        """

        if self.hotspot_fid is None:
            return
        if self.obj_black_vertices is None or self.obj_black_faces is None:
            return
        if self.obj_x is None or self.obj_y is None:
            return
        
        for i in range(0, len(self.hotspot_fid)):
            if test_color:
                color = 70 + i # kolor ściśle związany z wykrywaniem kliknięcia
            else:
                color = 60 # kolor ściśle związany z wykrywaniem kliknięcia
            glPushMatrix()
            glTranslatef(self.obj_x[i], self.obj_y[i], 0.301)  # Move 
            glBegin(GL_TRIANGLES)
            glColor3ub(color, color, color)
            for face in self.obj_black_faces:
                for vertex in face:
                    glVertex3fv([self.obj_black_vertices[vertex][0], self.obj_black_vertices[vertex][1], self.obj_black_vertices[vertex][2]])
            glColor3f(1, 1, 1) 
            glEnd() 
            glPopMatrix()    

    def drawHotSpots(self):
        """
        Rysowanie jasnych hot spotów w kolorze domyślnym
        """
        if self.hotspot_fid is None:
            return
        if self.obj_white_vertices is None or self.obj_white_faces is None:
            return
        if self.obj_x is None or self.obj_y is None:
            return
        
        for i in range(0, len(self.hotspot_fid)):
            glPushMatrix()
            glTranslatef(self.obj_x[i], self.obj_y[i], 0.3)  # Move 
            glBegin(GL_TRIANGLES)
            glColor3ub(220, 220, 220)
            for face in self.obj_white_faces:
                for vertex in face:
                    glVertex3fv([self.obj_white_vertices[vertex][0], self.obj_white_vertices[vertex][1], self.obj_white_vertices[vertex][2]])
            glColor3f(1, 1, 1) 
            glEnd() 
            glPopMatrix() 
    
    def testHotSpots(self):
        """
        Testuje kliknięcie w hot spot oraz wyzwala przeładowanie w przypadku trafienia
        """
        hot_spot_selected = -1

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()

        gluOrtho2D(0, self.viewport[2], self.viewport[3], 0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()    

        # aktualizacja danych o wymiarach viewport - przydaje się przy przerzucaniu okna między monitorami o różnym skalowaniu
        self.viewport = glGetIntegerv(GL_VIEWPORT) 

        # obsługa skalowania okien w Windows
        dpi_window_scale = float(self.viewport[3])/float(self.height())
        p_x = int(float(self.mouse_x) * dpi_window_scale)
        p_y = int(float(self.mouse_y) * dpi_window_scale)

        # pobranie punktu do testu
        # w cyklu są dwa wyświetlenia tej sekwencji - hot spot mruga i ta cecha odróżnia go od zdjęcia
        rgb = glReadPixels(p_x, self.viewport[3]-p_y, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE)
        if rgb[0] == rgb[1] and rgb[0] == rgb[2]: # interesuje nasz idealny ciemny szary
            # interesuje nas para 60 i 70+index, 60 to kolor spodu hotspotów
            if rgb[0] == 60 and self.hot_spot_last_rgb in range(70, 70+len(self.hotspot_fid)):
                hot_spot_selected = self.hotspot_fid[self.hot_spot_last_rgb-70]
            elif self.hot_spot_last_rgb == 60 and rgb[0] in range(70, 70+len(self.hotspot_fid)):
                hot_spot_selected = self.hotspot_fid[rgb[0]-70]
            self.hot_spot_last_rgb = rgb[0]
        else:
            self.hot_spot_last_rgb = 0

        # finalizacja GL
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        
        if self.hot_spot_test:
            self.hot_spot_test = False
            # wyzwalanie odświeżenia, które spowoduje wygenerowanie drugiej klatki porównawczej
            self.update()

        if hot_spot_selected != -1:
            self.parent.reloadView(hot_spot_selected)
            self.hot_spot_last_rgb = 0 # zapobieganie podwójnemu kliknięciu
            MessageUtils.pushLogInfo("Wybrano nowy punkt o indeksie fid: "+str(hot_spot_selected))  
        
    def updateViewerWidget(self, direction):
        """
        Ładuje na nowo zdjęcie do pamięci i wyzwala przeładowanie widoku
        """
        if self.is_widget_loaded:
            # self.yaw = direction
            self.loadTexture(self.nazwa_pliku)
            self.image_description_data = self.new_image_description_data
            self.update()
            return True
        else:
            MessageUtils.pushLogCritical("Aktualizacja widoku okna się nie powiodła.")
            return False 

    def setDataAboutPhoto(self, nazwa_pliku, data_wykonania, nr_drogi, nazwa_ulicy, numer_odcinka, kilometraz):
        """
        Wprowadza dane opisowe zdjęcia do Widgetu
        """
        self.data_wykonania = data_wykonania
        self.nr_drogi = nr_drogi
        self.nazwa_ulicy = nazwa_ulicy
        self.numer_odcinka = numer_odcinka
        self.kilometraz = kilometraz
        self.nazwa_pliku = nazwa_pliku

        try:
            image = Image.open(os.path.join(plugin_dir, "images", "desc_balloon.png"))
        except FileNotFoundError:
            MessageUtils.pushLogCritical("Nie znaleziono ścieżki /images/desc_balloon.png")
            return False
        except Exception:
            MessageUtils.pushLogCritical("Błąd podczas wczytywania zdjęcia /images/desc_balloon.png")
            return False
        
        try:
            font_regular = ImageFont.truetype(os.path.join(plugin_dir, "fonts", "Roboto_SemiCondensed-Regular.ttf"), 15)
            font_bold = ImageFont.truetype(os.path.join(plugin_dir, "fonts", "Roboto_SemiCondensed-Bold.ttf"), 15)
            # font_regular = ImageFont.truetype("arial.ttf", 15) # tylko Windows
            # font_bold = ImageFont.truetype("arialbd.ttf", 15)  # tylko Windows

        except FileNotFoundError:
            MessageUtils.pushLogCritical("Nie znaleziono plików czczionek.")
            return False
        except Exception:
            MessageUtils.pushLogCritical("Błąd podczas wczytywania plików czczionek.")
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

        if self.is_screen_shot_mode_activated:
            self.new_image_description_data = image.tobytes("raw", "RGB", 0, -1)
        else:
            self.new_image_description_data = image.tobytes("raw", "RGBA", 0, -1)
        return True

    def setHotSpots(self, coordinates):
        """
        Aktualizuje hotSpoty według podanej listy
        """
        self.coordinates = coordinates            

        if self.coordinates is not None:
            self.hotspot_fid = []
            self.obj_x = []
            self.obj_y = []
            scale = 0.104 # subiektywne skalowanie dystansu od obserwatora dla widoku OpenGL
            spectator_angle  = 0

            # określenie azymutu obserwatora
            for hotspot in self.coordinates:
                if hotspot['distance'] < 0.01:
                    spectator_angle = hotspot['azymut']
                    break

            # tworzenie listy koordynatów hotspotów w przestrzeni OpenGl
            for hotspot in self.coordinates:
                # pomijamy punkt obserwatora
                if hotspot['distance'] < 0.01:
                    continue

                self.hotspot_fid.append(hotspot['fid'])
                self.obj_x.append(scale*hotspot['distance']*math.cos(hotspot['azymut_obliczony'] + (270)*math.pi/180 - spectator_angle))
                self.obj_y.append(scale*hotspot['distance']*math.sin(hotspot['azymut_obliczony'] + (270)*math.pi/180 - spectator_angle))                   

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.width() / self.height(), 0.1, 1000)

    def updateRotationData(self, d_rotation, d_zoom, d_pitch):
        """
        Obraca obserwatora o podane delty i aktualizuje widok
        """
        self.yaw += d_rotation
        self.pitch -= d_pitch
        self.pitch = min(max(self.pitch, -90), 90)
        self.fov -= d_zoom
        self.fov = max(30, min(self.fov, 90))
        self.update()

    def mousePressEvent(self, event):
        if event.button() == self._QtCore_Qt_MouseButton_LeftButton:
            self.moving = False
            self.mouse_x, self.mouse_y = event.pos().x(), event.pos().y()
            self.setCursor(self._QtCore_Qt_CursorShape_ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        if not self.moving:
            
            # przeprowadzenie testu kliknięcia w hot spot
            self.hot_spot_test = True
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
        self.update()

        self.prev_dx = dx
        self.prev_dy = dy   
   
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.fov -= delta * 0.1
        self.fov = max(30, min(self.fov, 90))
        self.sensitivity = self.fov / 60
        self.update()

    def setScreenShotMode(self, state):
        """
        Wyłącza/włącza przezroczystości w obrazach, które nie zawsze poprawnie się zapisywały w pliku JPG/PNG
        """
        self.is_screen_shot_mode_activated = state
        self.setDataAboutPhoto(self.nazwa_pliku, self.data_wykonania, self.nr_drogi, self.nazwa_ulicy, self.numer_odcinka, self.kilometraz)
        self.image_description_data = self.new_image_description_data
        self.update()


