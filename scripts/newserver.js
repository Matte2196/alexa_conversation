var express = require("express");       //Express è necessario (per cosa?)
var app = express();
var path = require('path');
var bodyParser = require("body-parser");
app.use(bodyParser.urlencoded({ extended: false }));    //Da capire cosa fa
/*app.get("/", function(req, res) {
    res.end('Ciao! Sono il tuo server')
   // res.sendFile(path.join(__dirname + '/indexMatte.html'));      //Serve solo per la pagina html
});*/
app.post("/", function(req,res){        //Questo gestisce le richieste POST
    res.send('Sto funzionando');
    console.log('------------------------------');
    console.log("Ricevuto una richiesta POST");
    //console.log(req);
    console.log(req.body);              // contenuto della richiesta
    console.log('Il tipo di dato è:', typeof req.body);
    //var traducted = JSON.parse(req.body);
    //console.log(traducted);
    console.log('Username:', req.body.username);     // username
    console.log('Password:', req.body.pass);         // password
    console.log('------------------------------');
});
app.get("/", function(req,res){         //Questo gestisce le richieste GET
    console.log('------------------------------');
    res.send('Hai mandato una richiesta GET! Complimenti!');
    console.log("Ricevuta una richiesta GET");
    console.log(req.body);
    console.log('------------------------------');
});
var port = process.env.PORT || 5000;                //Creo un server sulla porta 5000
app.listen(port, function() {
    console.log("Listening on " + port);
});