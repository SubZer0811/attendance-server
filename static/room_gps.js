/*
	 * Use bindTo to allow dynamic drag of markers to refresh poly.
	 */

function MVCArrayBinder(mvcArray) {
	this.array_ = mvcArray;
}
MVCArrayBinder.prototype = new google.maps.MVCObject();
MVCArrayBinder.prototype.get = function (key) {
	if (!isNaN(parseInt(key))) {
		return this.array_.getAt(parseInt(key));
	} else {
		this.array_.get(key);
	}
}
MVCArrayBinder.prototype.set = function (key, val) {
	if (!isNaN(parseInt(key))) {
		this.array_.setAt(parseInt(key), val);
	} else {
		this.array_.set(key, val);
	}
}

var coords = [];

var poly;
var map;


function initialize() {
	var polyOptions = {
		strokeColor: '#000000',
		strokeOpacity: 1.0,
		strokeWeight: 3, map: map
	};
	poly = new google.maps.Polygon(polyOptions);
	var bounds = new google.maps.LatLngBounds();
	
	var cen_lat = 0, cen_lng = 0;
	for(i=0; i<coords.length; i+=1) {
		cen_lat += coords[i].lat();
		cen_lng += coords[i].lng();
	}
	cen_lat /= 4;
	cen_lng /= 4;
	
	map = new google.maps.Map(document.getElementById('map_canvas'), {
		center: new google.maps.LatLng(cen_lat, cen_lng),
		zoom: 30,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	});

	poly.binder = new MVCArrayBinder(poly.getPath());

	poly.setMap(map);

	for(var i=0; i<coords.length; i++) { 
		//coords.push(new google.maps.LatLng(10+i,
		//								   10+i));
		console.log(coords[i]);
		addLatLngDef(coords[i]);
	}
}

function addLatLngDef(coord) {
	var path = poly.getPath();
	path.push(coord);
	var len = path.getLength();
	console.log(coord)
	var marker = new google.maps.Marker({
		position: coord,
		title: '#' + len,
		map: map,
		draggable: true
	});
	google.maps.event.addListener(marker, 'drag', handleEvent);
	google.maps.event.addListener(marker, 'dragend', handleEvent);
	marker.bindTo('position', poly.binder, (len - 1).toString());
}

function handleEvent(event) {
	document.getElementById("changeBtn").hidden = "";
}

google.maps.event.addDomListener(window, "load", initialize);

function getCoords(id) {
	$.ajax({
		contentType : "application/json",
		dataType: "json",
		type: "POST",
		url: "/get_room/"+id,
		success: function(response) {
			console.log(response);
			coords = [];
			poly.setMap(null);
			console.log(parseFloat(response.gps_coord_1.split(",")[1]))
			coords.push(new google.maps.LatLng(
				parseFloat(response.gps_coord_1.split(",")[0]),
				parseFloat(response.gps_coord_1.split(",")[1])
				));
			coords.push(new google.maps.LatLng(
				parseFloat(response.gps_coord_2.split(",")[0]),
				parseFloat(response.gps_coord_2.split(",")[1])
				));
			coords.push(new google.maps.LatLng(
				parseFloat(response.gps_coord_3.split(",")[0]),
				parseFloat(response.gps_coord_3.split(",")[1])
				));
			coords.push(new google.maps.LatLng(
				parseFloat(response.gps_coord_4.split(",")[0]),
				parseFloat(response.gps_coord_4.split(",")[1])
				));
			initialize();

			document.getElementById("changeBtn").hidden = "hidden";
			cur_room = id;
		}
	});
}

cur_room = "";

function changeCoords() {
	formData = {
		gps_coord_1: ""+poly.getPath().getAt(0).lat()+","+poly.getPath().getAt(0).lng(),
		gps_coord_2: ""+poly.getPath().getAt(1).lat()+","+poly.getPath().getAt(1).lng(),
		gps_coord_3: ""+poly.getPath().getAt(2).lat()+","+poly.getPath().getAt(2).lng(),
		gps_coord_4: ""+poly.getPath().getAt(3).lat()+","+poly.getPath().getAt(3).lng()
	}
	$.ajax({
		contentType : "application/json",
		dataType: "json",
		type: "POST",
		url: "/change_room/"+cur_room,
		data: JSON.stringify(formData),
		success: function(response) {
			console.log(response);
			document.getElementById("changeBtn").hidden = "hidden";
		}
	  });

}