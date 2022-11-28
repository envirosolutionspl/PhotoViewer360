'use strict';
// Create viewer.
var viewer = new Marzipano.Viewer(document.getElementById('pano'));

// Create source.
var source = Marzipano.ImageUrlSource.fromString(
  "image.jpg"
);

// Create geometry.
var geometry = new Marzipano.EquirectGeometry([{ width: 8192 }]);

// Create view.
var limiter = Marzipano.RectilinearView.limit.traditional(8192, 100*Math.PI/180);

// stworzenie zmiennej odpowiedzialnej za umiejscowienie hotspot'u na zdjęciu 
var initialView = {
  yaw: 0 * Math.PI/180,
  pitch: 10 * Math.PI/180,
  fov: 90 * Math.PI/180
};

var view = new Marzipano.RectilinearView(initialView, limiter);

// Create scene.
var scene = viewer.createScene({
  source: source,
  geometry: geometry,
  view: view,
  pinFirstLevel: true
});

//Wyświetlanie informacji o zdjęciu
var fileMetadata = document.querySelector('#photo_data');
var fileToggleMetadata = document.querySelector('#file_metadata');

// Display scene.
scene.switchTo();

var viewChangeHandler = function() {
  var yaw = view.yaw();
	var d_yaw=yaw/(Math.PI/180)
	console.log('yaw= ' + d_yaw);
  };
 
view.addEventListener('change', viewChangeHandler);


const positions =[]
const coord_x =[]
const coord_y =[]
const index_list = []
const distance_list = []

// funkcja zmieniająca stopnie na radiany
function deg2rad(deg) {
  return deg * (Math.PI/180)
}

// odebranie parametrów zdjęcia z python'a
let data_coord = pythonSlot.getPhotoDetails();

// obliczanie pozycji hotspot'a na zdjęciu za pomocą parametrów z python'a
var aLines = data_coord.toString().split(",")
aLines.forEach(function(element){
    var coord = element.split(" ")
    if (coord[4] === '0.0'){  // wybranie danych dla punktu, w którym aktualnie jesteśmy (dla którego jest wyświetlane zdjęcie)
      var x = parseFloat(coord[0])
      var y = parseFloat(coord[1])
      var az = parseFloat(coord[2])
      for (let i=0; i<(aLines.length); i++){
        var coord = aLines[i].split(" ")
          if (coord[4]!='0.0'){ // wybranie pozostałych punktów
            var x1 = parseFloat(coord[0])
            coord_x.push(x1)
            var y1 = parseFloat(coord[1])
            coord_y.push(y1)
            var index = coord[3]
            index_list.push(index)
            var distance = parseFloat(coord[5])
            distance_list.push(distance)

            var position = ((360-az)*(Math.PI/180))+Math.atan2(x1-x,y1-y)
            positions.push(position)
          }
      }
    }
})

// zdefiniowanie wyglądu hotspot'a
for (let i=0; i<positions.length; i++) {
  var container = document.getElementById('container');
  if (distance_list[i] > 6.0 ){
    container.innerHTML += `<div id="link-hotspot"><img class="link-hotspot-icon" src="img/hotspot.png"  style="width: 80px"></div>`
  } 
  else {
    container.innerHTML += `<div id="link-hotspot"><img class="link-hotspot-icon" src="img/hotspot.png"  style="width: 120px"></div>`
  }
}
var list = document.querySelectorAll("#link-hotspot");

// stworzenie hotspotów
for (let i=0; i<list.length; i++) {
  scene.hotspotContainer().createHotspot(list[i], {yaw: positions[i],   pitch: (25-distance_list[i])*(Math.PI/180)});
  // obsługa kliknięcia w hotspot
  list[i].addEventListener('click', function() {

  // skomunikowanie się z python'em poprzez obiekt pythonSlot (przesłanie wspólrzędnych oraz indeksu punktu)
  pythonSlot.setXYtoPython(coord_x[i], coord_y[i], index_list[i]);
  var coord = document.getElementById('coord');
  coord.innerHTML += toString(x+","+y)
});
}

// DOM elements for view controls.
var viewUpElement = document.querySelector('#viewUp');
var viewDownElement = document.querySelector('#viewDown');
var viewLeftElement = document.querySelector('#viewLeft');
var viewRightElement = document.querySelector('#viewRight');
var viewInElement = document.querySelector('#viewIn');
var viewOutElement = document.querySelector('#viewOut');

// Dynamic parameters for controls.
var velocity = 0.7;
var friction = 3;

// Associate view controls with elements.
var controls = viewer.controls();
controls.registerMethod('upElement',    new Marzipano.ElementPressControlMethod(viewUpElement,     'y', -velocity, friction), true);
controls.registerMethod('downElement',  new Marzipano.ElementPressControlMethod(viewDownElement,   'y',  velocity, friction), true);
controls.registerMethod('leftElement',  new Marzipano.ElementPressControlMethod(viewLeftElement,   'x', -velocity, friction), true);
controls.registerMethod('rightElement', new Marzipano.ElementPressControlMethod(viewRightElement,  'x',  velocity, friction), true);
controls.registerMethod('inElement',    new Marzipano.ElementPressControlMethod(viewInElement,  'zoom', -velocity, friction), true);
controls.registerMethod('outElement',   new Marzipano.ElementPressControlMethod(viewOutElement, 'zoom',  velocity, friction), true);