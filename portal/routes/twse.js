var express = require('express');
var router = express.Router();

const grafanaUrl = {
	"prefix": "/grafana/dashboard-solo/db/summary?orgId=1&from=",
	"suffix": "&theme=light&panelId=1"
}

var epochTime = function (hour, minute){
	var newDate = new Date();
	newDate.setHours(hour, minute, 0, 0);
	return newDate.getTime();
};

/* GET users listing. */
router.get('/intraday', function(req, res, next) {
	// Get Stock from HTTP request
	var symbol = req.query.symbol;

	// Set the time range
	var marketOpen = epochTime(8, 30);
	var marketClosed = epochTime(13, 30);

	// Set the grafana url
	var url = grafanaUrl["prefix"] + marketOpen + "&to=" + marketClosed + "&var-channel=" + symbol + grafanaUrl["suffix"];
	res.render('intraday', { "grafana_url": url });
});

module.exports = router;
