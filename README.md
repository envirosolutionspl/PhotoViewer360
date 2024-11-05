# PhotoViewer360

## PL
Wtyczka umożliwiająca import i wizualizację zdjęć panoramicznych w programie QGIS. Oparta na wtyczce EquirectangularViewer.

## Funkcjonalność wtyczki
* import folderu ze zdjęciami posiadającymi georeferencję i utworzenie z nich pliku GeoPackage 
* przeglądanie zdjęć panoramicznych poprzez narzędzia do nawigacji oraz przy użyciu "łapki" oraz scrolla myszki
* orientacja w terenie dzięki radarowi na mapie umieszczonemu w punkcie, dla którego przeglądane jest zdjęcie
* wyświetlanie informacji nt. przeglądanego zdjęcia, tj: nr drogi, nazwa ulicy, nr odcinka, kilometraż i data wykonania
* możliwość przeglądania zdjęć w trybie pełnoekranowym
* przechodzenie pomiędzy zdjęciami poprzez wybór punktu na mapie bądź kliknięcie na hotspot podczas przeglądania zdjęcia
* możliwość wygenerowania raportu graficznego z aktualnym widokiem zdjęcia w formacie JPG/PNG

## Wymagania dot. importowanych zdjęć
* format zapisu rozszerzenia ".jpg"
* dane EXIF zawierające: szerokość i długość geograficzną, azymut kierunku głównego, datę wykonania
* nazwa zdjęć wg schematu: nrDrogi_nazwaUlicy_nrOdcinka_kilometraż
* importowane zdjęcia muszą znajdować się w jednym folderze, nie ma możliwości importu pojedynczego pliku

## Instrukcja użytkownika
1. Wtyczkę należy zainstalować w QGISie jako ZIP bądź wgrać pliki wtyczki do lokalizacji C:\Users\User\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins.
2. Aby uruchomić wtyczkę należy kliknąć na ikonę aparatu, co wywoła otwarcie okna do importu zdjęć panoramicznych.
3. Należy wybrać jedną z trzech opcji wgrania zdjęć do przeglądania:
    - Zakładka "Wybór zdjęć"- należy wybrać folder ze zdjęciami oraz ścieżkę zapisu nowego pliku GeoPackage. Następnie należy kliknąć na "Importuj", co utworzy plik .gpkg i uruchomi „celownik” – narzędzie do wskazania na mapie punktu,
    - Zakładka "Wybór warstwy w QGIS" - należy wskazać warstwę punktową, która dodana jest do projektu QGIS (utworzona wcześniej poprzez narzędzie z pierwszej zakładki wtyczki), a następnie kliknąć „Przeglądaj”, co uruchomi narzędzie „celownik”,
    - Zakładka "Wybór warstwy punktowej GPKG" - należy wskazać lokalizację na komputerze warstwy punktowej (utworzonej wcześniej poprzez narzędzie z pierwszej zakładki wtyczki), a następnie kliknąć „Przeglądaj”, co uruchomi narzędzie „celownik”.
4. Po wskazaniu bądź utworzeniu pliku GPKG uruchomi się narzędzie "celownik", a widok mapy przybliży się do pełnego zakresu warstwy. Fioletowym "celownikiem" należy kliknąć na wybrany punkt należący do warstwy punktowej, co otworzy okno wtyczki służące do przeglądania zdjęć panoramicznych. W momencie skorzystania z innego narzędzia poza wtyczką, w celu ponownego włączenia narzędzia "celownik", należy kliknąć na ikonę umieszczoną w górnym panelu QGISa (ikona po prawej stronie od głównej ikony wtyczki).
5. Wyświetlone zdjęcie panoramiczne można przeglądać posługując się narzędziami nawigującymi (strzałki, +, -) umieszczonymi w dolnej części okna wtyczki lub przesuwając obraz „łapką” oraz używając scrolla myszki do przybliżania i oddalania widoku. 
6. W celu przejścia do kolejnego zdjęcia można wybrać je poprzez kliknięcie punktu na mapie bądź kliknięcie jednego z wyświetlających się na zdjęciu hotspotów. Hotspoty są punktami znajdującymi się w promieniu 10 metrów od punktu aktualnie przeglądanego zdjęcia. Hotspot znajdujący się dalej niż 6 metrów od aktualnego punktu będzie miał mniejszy rozmiar.
7. W celu wygenerowania raportu graficznego należy z dolnej części wtyczki wybrać narzędzie z ikoną aparatu, a następnie wskazać lokalizację generowanego pliku oraz docelowy format.
8. Aby przeglądać zdjęcie w trybie pełnoekranowym należy wybrać drugie narzędzie z dolnej części wtyczki. W celu powrócenia do poprzedniego widoku należy ponownie kliknąć na ikonę narzędzia lub kliknąć przycisk ESC na klawiaturze.

## Uwaga
Warunkiem koniecznym do prawidłowego działania wtyczki jest posiadanie wersji QGIS 3.22 lub wyższej.
W celu poprawnego działania wtyczki PhotoViewer360, należy odinstalować wtyczkę EquirectangularViewer (jeśli była wcześniej zainstalowana).


# PhotoViewer360

# ENG
QGIS Plugin for importing and visualising local panoramic images. Based on EquirectangularViewer.

## Plugin functionality
* importing folder with geotagged panoramic photos and creating GeoPackage file with them
* viewing panoramic photos by navigation tool or with Pan Tool and mouse scroll
* orientation in the field thanks to the radar on the map placed at the point for which the photo is being viewed
* dispalying informations about: road number, name of the street, number of section, mileage and date the photo was taken
* the ability to view photos in full screen mode
* switching between photos by selecting a point on the map or clicking on the hotspot while viewing the photo
* ability of taking a creenshot with current view of photo

## Photo requirements
* extension saving format ".jpg"
* EXIF data containing: latitude and longitude, main direction azimuth, date the photo was taken
* name of photo according to the scheme: roadNumber_streetName_sectionNumber_mileage
* imported photos has to be in one folder, there is no ability to import a single file

## User manual
1. The plugin must be installed in QGIS from ZIP or by upload all files to C:\Users\User\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins.
2. To run the plugin, click on the camera icon, which will open the window for importing panoramic photos.
3. Choose one of the three options for uploading photos for viewing:
    - Tab "Wybór zdjęć" - select the folder with photos and the path to save the new GeoPackage file. Then click on "Importuj", which will create a .gpkg file and start the "viewfinder" - a tool for selecting a point on the map,
    - Tab "Wybór warstwy w QGIS" - indicate a point layer that has been added to the QGIS project (created earlier using the tool from the first tab of the plugin), then click on "Przeglądaj", which will start the "viewfinder",
    - Tab "Wybór warstwy punktowej GPKG" - indicate the location of the point layer on the computer (previously created using the tool from the first tab of the plugin), then click on "Przeglądaj", which will start the "viewfinder".
4. After selecting or creating a GPKG file, the "viewfinder" tool will be launched and the map view will zoom to the full range of the layer. With the violet "viewfinder", click on the selected point belonging to the point layer, which will open the plugin window for viewing panoramic photos. When using a tool other than the plugin, in order to reenable the "viewfinder" tool, click on the icon in the top panel of QGIS (the icon to the right of the plugin's main icon).
5. The displayed panoramic photo can be viewed using the navigation tools (arrows, +, -) located at the bottom of the plugin window or by moving the image with the Pan Tool and using the mouse scroll to zoom in and out.
6. In order to go to the next photo, you can select it by clicking a point on the map or clicking one of the hotspots displayed in the photo. Hotspots are points located within 10 meters from the point of the currently viewed photo. Hotspot more than 6 meters from the current point will be smaller.
7. In order to generate a graphic report, select the tool with the camera icon from the bottom of the plugin, and then indicate the location of the generated file and the target format.
8. To view a photo in full screen mode, select the second tool from the bottom of the plugin. To return to the previous view, click the tool icon again or click the ESC button on the keyboard.

## Attention
The necessary condition for the correct operation of the plugin is to have the QGIS 3.22 version or higher.
If the EquirectangularViewer plugin is installed, please uninstall it in order to the PhotoViewer360 plugin work properly.
