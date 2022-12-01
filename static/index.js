/*
 * Use bindTo to allow dynamic drag of markers to refresh poly.
 */

function MVCArrayBinder(mvcArray) {
	this.array_ = mvcArray;
  }
  MVCArrayBinder.prototype = new googlez.maps.MVCObject();
  MVCArrayBinder.prototype.get = function(key) {
	if (!isNaN(parseInt(key))) {
	  return this.array_.getAt(parseInt(key));
	} else {
	  this.array_.get(key);
	}
  }
  MVCArrayBinder.prototype.set = function(key, val) {
	if (!isNaN(parseInt(key))) {
	  this.array_.setAt(parseInt(key), val);
	} else {
	  this.array_.set(key, val);
	}
  }
  
  /**
   * Handles click events on a map, and adds a new point to the Polyline.
   * @param {MouseEvent} mouseEvent
   */
  function addLatLng(event) {
	var path = poly.getPath();
	path.push(event.latLng);
	var len = path.getLength();
	var marker = new google.maps.Marker({
	  position: event.latLng,
	  title: '#' + len,
	  map: map,
	  draggable: true
	});
	marker.bindTo('position', poly.binder, (len - 1).toString());
  }
  var locations = [
	[-33.890542, 151.274856, 4, 'Bondi Beach'],
	[-33.923036, 151.259052, 5, 'Coogee Beach'],
	[-34.028249, 151.157507, 3, 'Cronulla Beach'],
	[-33.80010128657071, 151.28747820854187, 2, 'Manly Beach'],
	[-33.950198, 151.259302, 1, 'Maroubra Beach']
  ];
  
  var poly;
  var map;
  
  function initialize() {
	var polyOptions = {
	  strokeColor: '#000000',
	  strokeOpacity: 1.0,
	  strokeWeight: 3,
	  map: map
	};
	poly = new google.maps.Polygon(polyOptions);
	var bounds = new google.maps.LatLngBounds();
	map = new google.maps.Map(document.getElementById('map_canvas'), {
	  center: new google.maps.LatLng(10.9386, -84.888),
	  zoom: 10,
	  mapTypeId: google.maps.MapTypeId.ROADMAP
	});
  
	poly.binder = new MVCArrayBinder(poly.getPath());
	for (var i = 0; i < locations.length; i++) {
	  var evt = {};
	  evt.latLng = new google.maps.LatLng(locations[i][0], locations[i][1]);
	  bounds.extend(evt.latLng);
	  addLatLng(evt);
	}
  
	poly.setMap(map);
	map.fitBounds(bounds);
  }
  
  google.maps.event.addDomListener(window, "load", initialize);