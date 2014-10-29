///////////////////////////////
//     TOPIC - jumbotron     //
///////////////////////////////
(function(){

	//////////////////////////////
	//       faces-slider     	//
	//////////////////////////////
	var slider = $('.slider-faces'),
			slide  = slider.find('.face'),
			faces, colors;

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

	// set active face
	function changeFace(index){

		var facesLeft = calcFacesLeft(index);

		slide.css('opacity', 0);

		setTimeout(function(){

			var cssOptions = {
				'width' : faces[index],
				'background-position' :  (facesLeft * -1),
				'opacity' : 1
			}

			if (getScreenWidth() > 992){
				cssOptions['left'] = facesLeft;
			}

			slide.css(cssOptions);
		},600);
	}

	// init loop
	setInterval(function(){
		topic
			.html(topics[counter])
			.css('color', colors[counter])
			.typewriter();

		changeFace(counter);

		counter = counter < topics.length-1 ? counter+1 : 0;

	},5000);

	// on page load
	topic.css('color', colors[0]).typewriter();
	changeFace(0);
	counter = 1;

})();


//////////////////////////
//       carousel     	//
//////////////////////////
(function(){

	var slider,
			slider_nav = $('.slider-nav'),
			slider_buttons = $('.slider-buttons');


	// onclick handler for slider nav
	function onClickSliderNav(e){
		var self = $(e.currentTarget);
		slider.slide(self.index());
	}

	// sets active state of slider nav
	function setActiveSliderNav(index){
		slider_nav.find('li')
							.removeClass('active')
							.eq(index)
							.addClass('active');
	}

	// onslide handler for slider
	function onSlideSlider(index, elem){
		setActiveSliderNav(index);
	}

	// onclick handler for slider buttons
	function onClickSliderButton(e){
		var self = $(e.currentTarget);

		if (self.hasClass('slider-button-left')){
			slider.prev();
		}else if (self.hasClass('slider-button-right')){
			slider.next();
		}else{
			// do nothing
		}
	}

	if (typeof Swipe !== 'undefined'){
		// init slider
		slider = Swipe(document.getElementById('slider'),{
			callback: onSlideSlider
		});
		// slider nav
		slider_nav.on('click', 'li', onClickSliderNav);
		// slider buttons
		slider_buttons.on('click','.slider-button', onClickSliderButton);
	}

})();