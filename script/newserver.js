var express = require("express");       //Express è necessario (per il server)
var app = express();
var path = require('path');
var bodyParser = require("body-parser");
var DB_json = require('./template.json');
var fs = require('fs');
//app.use(bodyParser.urlencoded({ extended: false }));    //Analizza il testo come dati codificati URL
app.use(bodyParser.json());

app.post("/", function(req,res){        //Questo gestisce le richieste POST
    res.send('SERVER MESSAGE: Sto funzionando');
    console.log('------------------------------');
    console.log("Ricevuto una richiesta POST");
    //console.log(req);
    console.log(req.body);              // contenuto della richiesta
    //console.log('Il tipo di dato è:', typeof req.body);
    //console.log('HEADERS -->', req.headers);
    console.log('Username:', req.body.username);     // username
    console.log('Password:', req.body.pass);         // password
    console.log('------------------------------');
});
app.get("/", function(req,res){         //Questo gestisce le richieste GET
    console.log('------------------------------');
    //res.send('Hai mandato una richiesta GET! Complimenti!');
    console.log("Ricevuta una richiesta GET");
    console.log(req.body);
    //res.send(DB_json.Robot.Status.Is_Working);
    DB_json.Robot.Status.Task_Selected=DB_json.Robot.Status.Task_Selected+1;
    console.log(DB_json.Robot.Status.Task_Selected)
    var mexage = JSON.stringify(DB_json.Robot.Status.Task_Selected)
    //res.send(mexage)
    res.send(DB_json)
    console.log('------------------------------');
});
var port = process.env.PORT || 5000;                //Creo un server sulla porta 5000
app.listen(port, function() {
    console.log("Listening on " + port);
    DB_json.Robot.Status.Is_Working=true;
    console.log(DB_json.Robot.Status)
});