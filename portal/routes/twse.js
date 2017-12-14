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
	var url = grafanaUrl["prefix"] + marketOpen + "&to=" + marketClosed + "&var-channel=" + symbol + grafanaUrl["suffix"];
	res.render('intraday', { "grafana_url": url });
});

module.exports = router;

// vim: ts=4 sw=4
