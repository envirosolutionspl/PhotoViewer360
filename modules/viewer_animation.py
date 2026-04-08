# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QTimer

from ..constants import (
    ANIMATION_FPS,
    ANIMATION_SLEEP_FPS,
    ANIMATION_ACCELERATION_FACTOR,
    ANIMATION_DECELERATION_FACTOR,
    ANIMATION_DEFAULT,
    ANIMATION_LOOK_DOWN,
    ANIMATION_LOOK_UP,
    ANIMATION_MAX_SPEED,
    ANIMATION_STOP,
    ANIMATION_TURN_LEFT,
    ANIMATION_TURN_RIGHT,
    ANIMATION_ZOOM_IN,
    ANIMATION_ZOOM_OUT
)

class ViewerAnimation():
    """ Klasa obsługująca obracanie widoku 3D za pomocą przycisków """

    def __init__(self):
        self._kierunek_obrotu = ANIMATION_DEFAULT
        self._predkosc_obrotu = ANIMATION_DEFAULT
        self._kierunek_podnoszenia = ANIMATION_DEFAULT
        self._predkosc_podnoszenia = ANIMATION_DEFAULT
        self._kierunek_przyblizania = ANIMATION_DEFAULT
        self._predkosc_przyblizania = ANIMATION_DEFAULT

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.viewAnimation)
        self._timer.start(int(1000 / ANIMATION_SLEEP_FPS))

        self._viewer_widget = None
      
    def connectWidgetToViewerAnimation(self, viewer_widget):
        self._viewer_widget = viewer_widget

    def startAnimation(self):
        if self._timer is not None:
            self._timer.start(int(1000 / ANIMATION_SLEEP_FPS))

    def stopAnimation(self):
        if self._timer.isActive():
            self._timer.stop()

    def turnLeft(self):
        self._kierunek_obrotu = ANIMATION_TURN_LEFT
        self._timer.setInterval(int(1000 / ANIMATION_FPS))

    def turnRight(self):
        self._kierunek_obrotu = ANIMATION_TURN_RIGHT
        self._timer.setInterval(int(1000 / ANIMATION_FPS))

    def turnStop(self):
        self._kierunek_obrotu = ANIMATION_STOP

    def zoomIn(self):
        self._kierunek_przyblizania= ANIMATION_ZOOM_IN
        self._timer.setInterval(int(1000 / ANIMATION_FPS))

    def zoomOut(self):
        self._kierunek_przyblizania= ANIMATION_ZOOM_OUT
        self._timer.setInterval(int(1000 / ANIMATION_FPS))

    def zoomStop(self):
        self._kierunek_przyblizania= ANIMATION_STOP

    def lookUp(self):
        self._kierunek_podnoszenia= ANIMATION_LOOK_UP
        self._timer.setInterval(int(1000 / ANIMATION_FPS))

    def lookDown(self):
        self._kierunek_podnoszenia= ANIMATION_LOOK_DOWN
        self._timer.setInterval(int(1000 / ANIMATION_FPS))

    def lookStop(self):
        self._kierunek_podnoszenia= ANIMATION_STOP

    def countRotationSpeed(self, kierunek, predkosc):
        """
        Oblicza nową prędkość obrotu dla animacji

        Parameters:
            kierunek - kierunek obrotu 
        Return:
            float - nowa prędkość
        """
        if kierunek != ANIMATION_STOP and abs(predkosc) < ANIMATION_MAX_SPEED:
            predkosc += ANIMATION_ACCELERATION_FACTOR * kierunek
        elif predkosc != 0.0:
            predkosc -= ANIMATION_DECELERATION_FACTOR * predkosc/abs(predkosc)
            if abs(predkosc) < ANIMATION_DECELERATION_FACTOR:
                predkosc = 0.0
        
        return predkosc


    def viewAnimation(self):
        """ Obliczenia prędkości obrotu i wyzwala aktualizację OpenGL """

        self._predkosc_obrotu = self.countRotationSpeed(
            self._kierunek_obrotu, self._predkosc_obrotu
        )
        self._predkosc_przyblizania = self.countRotationSpeed(
            self._kierunek_przyblizania, self._predkosc_przyblizania
        )
        self._predkosc_podnoszenia = self.countRotationSpeed(
            self._kierunek_podnoszenia, self._predkosc_podnoszenia
        )

        # wgrywamy nowe parametry do clasy OpenGL
        if self._viewer_widget is not None:
            self._viewer_widget.updateRotationData(
                self._predkosc_obrotu,
                self._predkosc_przyblizania,
                self._predkosc_podnoszenia,
            )

        if (
            self._predkosc_obrotu == 0
            and self._predkosc_przyblizania == 0
            and self._predkosc_podnoszenia == 0
        ):
            self._timer.setInterval(int(1000 / ANIMATION_SLEEP_FPS))