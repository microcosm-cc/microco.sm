function updateTimes() {
	$('time').each(function(i) {
		var t = $(this);
		var dt = t.attr('datetime');
		if (dt && dt.trim() != '') {
			var m = moment(dt);
			var f = t.attr('format');
			// Relative date for simplicity
			var td = (f && f.trim() != '') ? m.format(f) : m.fromNow();
			if (t.text() != td) {
				t.text(td);
			}
			// Tooltip for precise date
			var tt = t.attr('title');
			var tip = m.format('LLLL');
			if (!tt || tt != tip) {
				t.attr('title', tip);
			}
		}
	});
}
if (jQuery && moment) {
	updateTimes();
}

$('document').ready(function() {
	// Updates <time> to use relative times
	updateTimes();
	setInterval(updateTimes, 60000); // Update every minute


	// Make code look pretty
	$('pre > code').addClass('prettyprint')
			.parent().addClass('prettyprint').addClass('linenums');

	var acceptedLangs = ["bsh", "c", "cc", "cpp", "cs", "csh", "cyc", "cv", "htm", "html", "java", "js", "m", "mxml", "perl", "pl", "pm", "py", "rb", "sh", "xhtml", "xml", "xsl"];

	$('pre.prettyprint').each(function(index) {
		var lang = $(this).attr('lang');

		if (typeof lang !== 'undefined' && lang != '' && $.inArray(lang, acceptedLangs) > -1) {
			$(this).addClass('lang-' + lang);
		}
	});
	
	prettyPrint();


	// Make tables in user generated content look pretty
	$('.ugc table').addClass('table').addClass('table-hover');
});
