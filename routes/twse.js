const async = require('async')
const fs = require('fs')
const json2csv = require('json2csv')
const moment = require('moment')
const pysh = require('python-shell')
const uuid = require('uuid/v4')

// Express router
const express = require('express')
var router = express.Router()

// MariaDB client
const mariadb = new require('mariasql')({
    host: "localhost",
    user: "ness",
    password: "ness",
    db: "ness",
    charset :"utf8"
})

// InfluxDB client
const InfluxDB = require("influx").InfluxDB
const influx = new InfluxDB({
    host: 'localhost',
    database: 'ness'
})

var EpochTime = function (hour, minute){
    /*
        This function is used to generate epochtime with specific time.
    */
    var newDate = new Date()
    newDate.setHours(hour, minute, 0, 0)
    return newDate.getTime()*1000*1000
}

var DateToEpochTime = function (dateString) {
    /*
        This function is used to convert time from string to epochtime.
    */
    var patten = /(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/
    var date = new Date(dateString.replace(patten, "$1-$2-$3T$4:$5:$6Z"))
    return date.getTime()*1000*1000
}

var DateRangeToEpochTime = function (startDateString, endDateString){
    /*
        This function is used to convert the time range from string to epochtime.
        If the time string is null, auto create a time with local time
    */

    var dateRange = [startDateString, endDateString]
    for (var i=0; i<2; i++){
        if (dateRange[i] != null)
            dateRange[i] = DateToEpochTime(dateRange[i])
        else{
            if (i==0)
                // The market is open at 9:00
                dateRange[i] = EpochTime(9, 0)
            else
                // The market is closed at 13:30
                dateRange[i] = EpochTime(13, 30)
        }
    }

    return dateRange
}

var DataSrcFile = function (data){
    /*
        This function is used to generate a temporary file to store data
    */
    var filename = '/tmp/ness-' + uuid()
    fs.writeFileSync(filename, data, (err) => {
        if (err){
            console.log(err)
            return null
        }
    })
    return filename
}

var StockName = function (tag, callback){
    /*
        This function is used to query stock name and channel (symbol) from MariaDB, 
        and pass result to the callback funtion.
    */
    const sql = "select symbol,name from stock_list where tag = '" + tag + "'"
    var stocks = new Object()
    mariadb.query(sql, (err, results) => {
        if (err){
            console.log(err)
            callback(err, null)
        }else{
            /* Convert result from array to a key-value object */
            results.forEach(result => {
                stocks[result.symbol] = result.name
            })
            callback(null, stocks)
        }
    })
    mariadb.end()
}

var Strategy_1 = function(req, callback){
    /*
        This is a strategy funciton named with its strategy id.

        In the arguments, the first arguemnt is reuqest object get from '/strategy' route,
        and this funciton will get the required data by itself.
        The second argument is a callback function used to pass the results (and error) back to the '/strategy route'
    */

    /* Get requred data from request */
    var primary = req.query.primary
    var secondary = req.query.secondary
    var [start, end] = DateRangeToEpochTime(req.query.start, req.query.end)

    /* Query stock data and start to analysing with external analyzer */
    var qs = "select channel,price from twse where time >= " + start + " and time <= " + end + 
        " and channel =~ /" + primary + "|" + secondary + "/"
    influx.query(qs).then(stocks =>{
        // Prepare Python runtime environment
        var dataFile = DataSrcFile(JSON.stringify(stocks))
        var options = {
            mode: 'json',
            pythonPath: '/usr/bin/python3',
            pythonOptions: '-u',
            scriptPath: 'external_modules/analyzers/strategy',
            args: [primary, secondary, dataFile]
        }

        // Run Python program to analysis stock
        pysh.run("strategy_1.py", options, function(err, results) {
            callback(err, results)
        })
    })

}

router.get('/stocks', function (req, res, next) {
    /*
        This route is usd to get the mapping of the name and channel of stocks
        User should pass a time range to limit the range of stock data.

        In this platform, we using MariaDB to store cold data, like the concept stock of tw0050, ... etc.
        And using InfluxDB to store hot data like stock price in every seconds.

        To get the stock list (name and channel mapping) with a specific time range,
        we query data from both these two differnt database, 
        and using the channel list queried from InfluxDB as the primary data,
        then mapping the name list queried from MariaDB to channel list to get the stock list for user.
    */

    res.setHeader('Content-Type', 'application/json')

    /* Get the required data from request */
    const tag = req.query.tag || 'tw0050'
    const [start, end] = DateRangeToEpochTime(req.query.start, req.query.end)

    async.series([
        function(next){
            /* Query data from MariaDB */
            StockName(tag, function(err, results){
                next(null, results)
            })
        },
        function(next){
            /* Query data from Influx DB */
            const qs = 'show tag values from twse with key in ("channel") where time >= ' + 
                start + " and time <= " + end
            influx.query(qs).then(results => {
                next(null, results)
            })
        }
    ], function(errs, results){
        /* Merge two data and make stock list with mapping the stock name and stock channel */
        var [name, channels] = results
        var stocks = new Array()
        channels.forEach(channel => {
            stocks.push({"label": name[channel["value"]], "value": channel["value"]})
        })
        res.json(stocks)
    })
})

router.get('/strategy', function(req, res, next){
    /*
        This route used to forwrad user request to strategy funciton,
        and return respone to user with the result of strategy.

        To use this route, user must pass the id of strategy and the required data in the reuqest.
    */
    res.setHeader('Content-Type', 'application/json')
    var strategyID = req.query.id || 0

    switch (parseInt(strategyID)){
        case 1:
            /* Pass a callback function that we can handle the results and error of strategy */
            Strategy_1(req, function(err, results){
                if (err){
                    console.log(err)
                    return res.json({})
                }
                res.json(results[0])
            })
            break
        default:
            res.json({})
    }
})

router.get('/stock/intraday', function(req, res, next){
    var format = req.query.format || "json"

    var qs = "select channel,price from twse"
    influx.query(qs).then(stocks =>{
        if (format == "csv"){
            var fields = ["time"]
            var data = []
            for (var i=0; i<stocks.length ; i++){
                var time = new Date(stocks[i].time)
                time = moment(time).format("YYYY/MM/DD hh:mm:ss")
                var channel = stocks[i]["channel"]
                var price = stocks[i]["price"]
                var last = data.length - 1 
                if (data.length > 0 && data[last]["time"] == time)
                    data[last][channel] = price
                else{
                    var stock = {time: time}
                    stock[channel] = price
                    data.push(stock)
                }

                if (fields.indexOf(channel) === -1)
                    fields.push(channel)
            }
            res.setHeader('Content-Type', 'application/csv')
            res.attachment('twse-intraday.csv');
            res.send(json2csv({data: data, fields: fields}))
        }else{
            res.setHeader('Content-Type', 'application/json')
            res.json(stocks)
        }
    })
})

module.exports = router

// vim: ts=4 sw=4 expandtab
