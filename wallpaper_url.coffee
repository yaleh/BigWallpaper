jsdom = require 'jsdom'

jsdom.env 'http://www.boston.com/bigpicture', \
	['http://code.jquery.com/jquery-1.5.min.js'], \
	(errors, window) ->
		console.log (window.$ "img.bpImage")[0].src