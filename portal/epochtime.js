var epochTime = function (hour, minute){
	var newDate = new Date();
	newDate.setHours(hour, minute, 0, 0);
	return newDate.getTime();
};

module.exports = epochTime;
