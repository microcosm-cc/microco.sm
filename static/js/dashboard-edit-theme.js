(function(){

	var form = $('#form-theme');


	//////////////////////////////
	//		BACKGROUND		    //
	//							//
	//////////////////////////////

	var el_bg = $('.dashboard');

	var theme_defaults = {
		'background-image'		: 'none',
		'background-position'	: '0 0',
		'background-size'		: 'inherit',
		'background-repeat'		: 'no-repeat'
	}

	var theme_user = $.extend({},theme_defaults);

	function applyThemeBg(new_theme){
		var theme;
		theme = $.extend({},theme_defaults, new_theme);
		el_bg.css(theme);
	}

	// calcs background image
	function getBackgroundImage(backgroundImage){
		var bg;

		bg = {
			'background-image' : 'url("'+backgroundImage+'")'
		}

		return bg;
	}

	// calcs background color
	function getBackgroundColor(backgroundColor){
		var bg;

		bg = {
			'background-color' : backgroundColor
		}

		return bg;
	}

	// calcs background-size, background-repeat, background-position
	function getBackgroundModifier(backgroundModifier){

		var bg;

		bg = {
			'background-size'    : 'inherit',
			'background-repeat'  : 'repeat',
			'background-position': '0 0'
		}

		switch(backgroundModifier){
			case 'tile': // tiling
				bg['background-size']		= 'inherit';
				bg['background-repeat']		= 'repeat';
				bg['background-position']	= '0 0';
				break;
			case 'cover': // stretch
				bg['background-size']		= 'cover';
				bg['background-repeat']		= 'no-repeat';
				bg['background-position']	= '0 0';
				break;
			case 'left': // position-left
				bg['background-size']		= 'inherit';
				bg['background-repeat']		= 'no-repeat';
				bg['background-position']	= '0 0';
				break;
			case 'center': // position-center
				bg['background-size']		= 'inherit';
				bg['background-repeat']		= 'no-repeat';
				bg['background-position']	= 'center 0';
				break;
			case 'right': // position-right
				bg['background-size']		= 'inherit';
				bg['background-repeat']		= 'no-repeat';
				bg['background-position']	= 'right 0';
				break;
			default:
				break;
		}
		return bg;
	}

	// apply bg image styles
	function applyBackgroundImage(value){
		theme_user = $.extend({}, theme_user, getBackgroundImage(value) );
		applyThemeBg(theme_user);
	}
	// apply bg color styles
	function applyBackgroundColor(value){
		theme_user = $.extend({}, theme_user, getBackgroundColor(value) );
		applyThemeBg(theme_user);
	}
	// apply bg modifier styles
	function applyBackgroundModifer(value){
		theme_user = $.extend({}, theme_user, getBackgroundModifier(value) );
		applyThemeBg(theme_user);
	}
	// reset background
	function resetBackground(){
		theme_user = $.extend({}, theme_defaults);
		applyThemeBg(theme_user);
		replaceInputBgImage();
	}
	// destroys current input <file> and replaces with new one
	// only way to clear just the <file>
	function replaceInputBgImage(){
		form.find('#input_bg_image').replaceWith('<input type="file" id="input_bg_image" />');
	}

	//////////////////////////////
	//							//
	//		    BIND        	//
	//							//
	//////////////////////////////

	// updates bg image placeholder above input bg image <input>
	function updateInputBgImagePlaceholder(source){
		$('.input_bg_image_placeholder').css('background-image', 'url("'+source+'")');
	}
	function clearInputBgImagePlaceholder(){
		$('.input_bg_image_placeholder').css('background-image', 'none');
	}

	// fires when <input> input bg image is changed
	// updates .dashboard background and input bg image placholder
	function onChangeInputBgImage(e){
		var self = $(e.currentTarget),
				files = self.context.files,
				current_file;

		if (files.length > 0){
			current_file = files[0];

			if (current_file.type.match('image.*')){

        reader = new FileReader();

        reader.onload = function(e){
        	var dataurl = e.target.result;
        	applyBackgroundImage(dataurl);
        	updateInputBgImagePlaceholder(dataurl);
        };
        reader.readAsDataURL(current_file);
      }
    }
	}

	// reset background
	function onClickInputBgImageRemove(e){
		e.preventDefault();
		resetBackground();
		clearInputBgImagePlaceholder();
	}

	// fires on the radio input changes
	function onChangeInputBgModifier(e){
		var self = $(e.currentTarget);
		applyBackgroundModifer(self.val());
	}

	form.on('change', '#input_bg_image', onChangeInputBgImage);
	form.on('click', '#input_bg_image_remove', onClickInputBgImageRemove);
	form.on('change', 'input[name=bg_position]', onChangeInputBgModifier);


	//////////////////////////////////////////////////////
	//	EVERYTHING THAT ISNT TO DO WITH THE BG IMAGE	//
	//////////////////////////////////////////////////////

	function onChangeColorColorpicker(e){
		var self = $(e.currentTarget),
				preview = self.parent().find('.colorpicker-preview');
		if (preview.length > 0){
			preview.css('background-color', e.color.toHex());
		}
	}

	function onChangeColorpicker(e){
		var self = $(e.currentTarget),
				preview = self.parent().find('.colorpicker-preview');
		if (preview.length > 0){
			preview.css('background-color', self.val());
		}
	}

	function onclickColorpickerPreview(e){
		var self = $(e.currentTarget),
				widget = self.parent().find('.colorpicker-widget');
		if (widget.length > 0){
			widget.colorpicker('show');
		}
	}

	form.find('.colorpicker-widget')
		.colorpicker({format: 'hex'})
		.on('changeColor', onChangeColorColorpicker)
		.on('change', onChangeColorpicker);

	form.on('click', '.colorpicker-preview', onclickColorpickerPreview);


	// <input> specific

	function onChangeInputBgColor(e){
		applyBackgroundColor( e.color.toHex() );
	}
	function onChangeInputLinkColor(e){
		$('.dashboard-container').find('a:not(.btn)').css('color', e.color.toHex());
	}
	function onChangeInputOverlayColor(e){
		$('.dashboard-container').css('background-color',e.color.toHex());
	}

	$('#input_bg_color').on('changeColor', onChangeInputBgColor);
	$('#input_link_color').on('changeColor', onChangeInputLinkColor);
	$('#input_overlay_color').on('changeColor', onChangeInputOverlayColor);

})();

