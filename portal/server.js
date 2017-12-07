var express = require('express')
var mysql = require('mysql');
var pug = require('pug')
var epochtime = require('./epochtime');

var fs = require('fs');
var app = express()

app.set('view engine', 'pug');
app.get('/', function (req, res) {
	var responseText = 'Hello World!'
	res.send(responseText)
})

app.use('/css', express.static('css'));
app.get('/intraday', function(req, res){
	// Set the time range
	var marketOpen = epochtime(8, 30);
	var marketClosed = epochtime(13, 30);

	// Set the grafana url
	var grafana_url = "http://" +  req.get('host') +":3000/dashboard-solo/db/intraday?orgId=1&panelId=1&from=" + marketOpen + ".&to=" + marketClosed + "&theme=light"

	// response
	res.send(pug.renderFile('templates/intraday.pug', {
		"grafana_url": grafana_url
	}));
})

app.listen(80)

// vim: ts=4 sw=4
