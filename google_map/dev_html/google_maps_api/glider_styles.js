      // Define icons to use
      icons = {
        lastPosnIcon : {
	  name : 'Current',
	  icon : {
	     url: 'http://imsdockserver.dyndns.org/realtime/tracks/icons/grn-circle.png',
	     // This marker is the default paddle and is 64 x 64 pixels.  
	     // Scale it down.
	     scaledSize: new google.maps.Size(32, 32),
	     },
	  },
        lastWayPosnIcon : { 
	  name : 'Next Waypoint',
	  icon :{
	     url: 'http://imsdockserver.dyndns.org/realtime/tracks/icons/grn-square-lv.png',
	     // This marker is 16 pixels wide by 16 pixels high.
	     // The anchor for this image is at the center (7, 7) of scaled size.
	     anchor: new google.maps.Point(7, 7)
	     },
	   },
        prevPosnIcon : {
	  name : 'Previous',
	  icon : {
	     url: 'http://imsdockserver.dyndns.org/realtime/tracks/icons/ylw-circle-lv.png',
	     // This marker is 16 pixels wide by 16 pixels high.
	     // The anchor for this image is at the center (7, 7) of scaled size.
	     anchor: new google.maps.Point(7, 7)
	     },
	   },
        gotoPosnIcon : {
	  name : 'Goto Waypoint',
	  icon : {
             url: 'http://imsdockserver.dyndns.org/realtime/tracks/icons/wht-blank-lv.png',
	     // This marker is 16 pixels wide by 16 pixels high.
	     // The anchor for this image is at the center (7, 7) of scaled size.
	     anchor: new google.maps.Point(7, 7)
	     }
	   }
	};

      // Define colors to use
      colors = {
        gliderBlueLine : {
	  color : 'blue',
	  },
        gliderGreenLine : {
	  color : 'green',
	  },
        gliderBlackLine : {
	  color : 'black',
	  }
	};
