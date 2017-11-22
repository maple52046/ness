var express = require('express')
var mysql = require('mysql');
var pug = require('pug')

var fs = require('fs');
var app = express()

var sql = "select t,y,o,h,l,z,b,g,a,f,v,tv,u,w from stock;"

app.set('view engine', 'pug');
app.get('/', function (req, res) {
	var responseText = 'Hello World!'
	res.send(responseText)
})

app.use('/css', express.static('css'));
app.get('/stock', function(req, res){
	var con = mysql.createConnection({
		host: "localhost",
		user: "ness",
		password: "ness",
		database: "ness"
	});
	var recordList = [];

	con.connect(function(err){
		if (err) throw err;
	})

	con.query(sql, function(err, result){
		if (err) throw err;
		for (var i=0; i<result.length; i++){
			var record = {
				't': result[i].t,
				'y': result[i].y,
				'o': result[i].o,
				'h': result[i].h,
				'l': result[i].l,
				'z': result[i].z,
				'b': result[i].b,
				'g': result[i].g,
				'a': result[i].a,
				'f': result[i].f,
				'v': result[i].v,
				'tv': result[i].tv,
				'u': result[i].u,
				'w': result[i].w
			}
			recordList.push(record)
		}
		res.send(pug.renderFile('templates/stock.pug', {
			"stock": '1101',
			"records": recordList
		}))

	})

	con.end()
})

app.listen(80)

// vim: ts=4 sw=4
