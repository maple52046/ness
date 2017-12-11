var express = require('express');
var router = express.Router();

var epochTime = function (hour, minute){
	var newDate = new Date();
	newDate.setHours(hour, minute, 0, 0);
	return newDate.getTime();
};


/* GET users listing. */
router.get('/', function(req, res, next) {
	// Set the time range
	var marketOpen = epochTime(8, 30);
	var marketClosed = epochTime(13, 30);

	// Set the grafana url
	var url = "/grafana/dashboard-solo/db/intraday?orgId=1&from=" + marketOpen + "&to=" + marketClosed + "&panelId=1&theme=light"
	res.render('intraday', { "grafana_url": url });
});

module.exports = router;
