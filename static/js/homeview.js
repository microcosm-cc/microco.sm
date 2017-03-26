///////////////////////////////
//     TOPIC - jumbotron     //
///////////////////////////////
(function(){

	var topic = $('.topic'),
			counter = 1;

	var topics = [
		'your interests',
		'fixed-gear cycling',
		'bread baking',
		'fly fishing in Kent',
		'Jaguar E-Type owners',
		'raspberry pi users',
		'record collecting',
		'watch collecting'
	];

	// widths of each face
	faces=[
		123,
		116,
		128,
		130,
		116,
		116,
	 	167,
		126
	];

	colors=[
		'#ff6d6d', // red orange
		'#ffa63d', // orange
		'#6fe2d0', // light greenish
		'#00c0ff', // blue cyan
		'#a77fd7', // purple
		'#98786d', // brown
		'#8aa75c', // dark green
		'#ed81cd'  // dusky pink
	];


	function getScreenWidth(){
		return $('body').width();
	}

	// acculates each previous face's width to give a left offset
	function calcFacesLeft(index){
		var i=0,j=index,retval = 0;

		for(;i<j;i++){
			retval = retval + faces[i];
		}
		return retval;
	}

	// init loop
	setInterval(function(){
		topic
			.html(topics[counter])
			.css('color', colors[counter]);

		counter = counter < topics.length-1 ? counter+1 : 0;

	},5000);

	// on page load
	topic.css('color', colors[0]);
	counter = 1;

})();
