const express = require('express')
var router = express.Router()
const fs = require('fs')
const uuid = require('uuid/v4')
const async = require('async');

// MariaDB client
const mariadbClient = require('mariasql')
const mariadb = new mariadbClient({
	host: "localhost",
	user: "ness",
	password: "ness",
	db: "ness",
	charset :"utf8"
})

// InfluxDB client
const Influx = require("influx")
const influx = new Influx.InfluxDB({
	host: 'localhost',
	database: 'ness'
})

// Python shell
const pysh = require('python-shell')

// Epothtime function
var epochTime = function (hour, minute){
	var newDate = new Date()
	newDate.setHours(hour, minute, 0, 0)
	return newDate.getTime()*1000*1000
}

var dateToEpochTime = function (dateString) {
	var patten = /(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/
	var date = new Date(dateString.replace(patten, "$1-$2-$3T$4:$5:$6Z"))
	return date.getTime()*1000*1000
}

var dateRangeToEpochTime = function (startDateString, endDateString){
	/* If the string of start date is null, using today's moring (9:00) as the start date*/
	if (startDateString != null){
		var start = dateToEpochTime(startDateString)
	}else{
		var start = marketOpen = epochTime(9, 0)
	}

	/* If the string of end date is null, using today's afternoon (13:30) as the end date*/
	if (endDateString != null){
		var end = dateToEpochTime(endDateString)
	}else{
		var end = epochTime(13, 30)
	}

	return [start, end]
}

var tmpFile = function (data){
	var filePath = '/tmp/ness-' + uuid()
	fs.writeFile(filePath, data, (err) => {
		if (err){
			console.log(err);
		}
	})
	return filePath
}

const grafanaUrl = {
	"prefix": "/grafana/dashboard-solo/db/summary?orgId=1&from=",
	"suffix": "&theme=light&panelId=1"
}


var StockName = function (tag, callback){
	const sql = "select symbol,name from stock_list where tag = '" + tag + "'"
	var stocks = new Object()
	mariadb.query(sql, (err, results) => {
		if (err){
			console.log(err)
			callback(err, null)
		}else{
			results.forEach(result => {
				stocks[result.symbol] = result.name
			})
			callback(null, stocks)
		}
	})
	mariadb.end()
}

router.get('/stocks', function (req, res, next) {
	res.setHeader('Content-Type', 'application/json')

	/* Get stock name and channel from MariaDB (with tag name) */
	const tag = req.query.tag || 'tw0050'
	const [start, end] = dateRangeToEpochTime(req.query.start, req.query.end)

	async.series([
		function(next){
			StockName(tag, function(err, stocks){
				next(null, stocks)
			})
		},
		function(next){
			const qs = 'show tag values from twse with key in ("channel") where time >= ' + start + " and time <= " + end
			influx.query(qs).then(results => {
				next(null, results)
			})
		}
	], function(errs, results){
		var [stocks, channels] = results
		var stockList = new Array()
		channels.forEach(channel => {
			stockList.push({"label": stocks[channel["value"]], "value": channel["value"]})
		})
		res.json(stockList)
	})

})

router.get('/intraday', function(req, res, next) {
	// Get Stock from HTTP request
	var symbol = req.query.symbol

	// Set the time range
	var marketOpen = epochTime(9, 0)
	var marketClosed = epochTime(13, 30)

	// Set the grafana url
	var url = grafanaUrl["prefix"] + marketOpen + "&to=" + marketClosed + 
		"&var-channel=" + symbol + grafanaUrl["suffix"]
	res.render('intraday', { "grafana_url": url })
})

router.get('/strategy', function(req, res, next){
	res.setHeader('Content-Type', 'application/json')
	var primary = req.query.primary
	var secondary = req.query.secondary
	var [start, end] = dateRangeToEpochTime(req.query.start, req.query.end)
	//var stockObj = {}

	// Generate InfluxDB query command
	var queryString = "select channel,price from twse where time >= " + start + " and time <= " + end + " and channel =~ /" + primary + "|" + secondary + "/"
	console.log(queryString)
	influx.query(queryString).then(stockPrices => {

		//res.json(stockPrices)

		// Prepare Python runtime environment
		var dataFile = tmpFile(JSON.stringify(stockPrices))
		var options = {
			mode: 'json',
			pythonPath: '/usr/bin/python3',
			pythonOptions: '-u',
			scriptPath: 'external_modules/',
			args: [primary, secondary, dataFile]
		}

		// Run Python program to analysis stock
		pysh.run('analyzers/algorithm/pair.py', options, function(err, results) {
			if (err) {
				console.log(err)
				res.json({})
			}
			res.json(results[0])
		})
	})
})

module.exports = router

// vim: ts=4 sw=4
