var express = require('express');
var router = express.Router();

var mariadbClient = require('mariasql');
const mariadb = new mariadbClient({
	host: "localhost",
	user: "ness",
	password: "ness",
	db: "ness",
	charset :"utf8"
});

const Influx = require("influx");
const influx = new Influx.InfluxDB({
	host: 'localhost',
	database: 'ness'
});

var pysh = require('python-shell');

const grafanaUrl = {
	"prefix": "/grafana/dashboard-solo/db/summary?orgId=1&from=",
	"suffix": "&theme=light&panelId=1"
}

var epochTime = function (hour, minute){
	var newDate = new Date();
	newDate.setHours(hour, minute, 0, 0);
	return newDate.getTime();
};

router.get('/stocks', function (req, res, next) {
	// Set response is a JSON data
	res.setHeader('Content-Type', 'application/json');

	// Query stock list from MariaDB
	const sql = "select symbol,name from stock_list where tag = 'tw0050'";
	mariadb.query(sql, (err, results) => {
		if (err){
			console.log(err);
			// Return an empty json object when query is fault.	
			res.json({});
			return;
		}
		res.json(results);
	});
});

router.get('/intraday', function(req, res, next) {
	// Get Stock from HTTP request
	var symbol = req.query.symbol;

	// Set the time range
	var marketOpen = epochTime(9, 0);
	var marketClosed = epochTime(13, 30);

	// Set the grafana url
	var url = grafanaUrl["prefix"] + marketOpen + "&to=" + marketClosed + 
		"&var-channel=" + symbol + grafanaUrl["suffix"];
	res.render('intraday', { "grafana_url": url });
});

var dateToEpochTime = function (dateString) {

	var patten = /(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/;
	var date = new Date(dateString.replace(patten, "$1-$2-$3T$4:$5:$6Z"));
	return date.getTime()*1000*1000;
	
}

var dateRangeToEpochTime = function (startDateString, endDateString){
	return [dateToEpochTime(startDateString), dateToEpochTime(endDateString)];
}

router.get('/backtest', function(req, res, next){
	// time range
	var start = dateToEpochTime(req.query.start);
	var end = dateToEpochTime(req.query.end);

	// symbol
	var symbol = req.query.symbol.split('-');

	// get data from database
	var queryString = "select channel, price from twse where time >= " + start + " and time <= " + end + 
		" and (channel = '" + symbol[0] + "' or channel = '" + symbol[1] + "')";
	influx.query(queryString).then(stocks => {
		var options = {
			mode: 'json',
			pythonPath: '/usr/bin/python3',
			pythonOptions: '-u',
			scriptPath: '/home/ubuntu/ness/data/analyzer',
			args: [JSON.stringify(stocks)]
		};

		pysh.run('stretage.py', options, function(err, results) {
			//if (err) res.json({});
			res.json(results);
		});
	});
	//res.send(queryString);
});

router.get('/backtest/pair', function(req, res, next){
	var [start, end] = dateRangeToEpochTime(req.query.start, req.query.end);
	var queryString = "select channel,price from twse where time >= " + start + " and time <= " + end;
	var stockObj = {};
	influx.query(queryString).then(stocks => {
		stocks.forEach(function(stock){
			var price = parseFloat(stock['price']);
			var channel = stock['channel'];
			if (stockObj.hasOwnProperty(channel) == true){
				if (stockObj[channel] < price){
					stockObj[channel] = price;
				}
			}else{
				stockObj[channel] = price;
			}
		});

		var options = {
			mode: 'json',
			pythonPath: '/usr/bin/python3',
			pythonOptions: '-u',
			scriptPath: '/home/ubuntu/ness/data/analyzer/algorithm',
			args: [JSON.stringify(stockObj)]
		};

		pysh.run('pair.py', options, function(err, results) {
			res.json(results);
		});
	});
});

module.exports = router;

// vim: ts=4 sw=4
