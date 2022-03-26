var express = require("express");       //Express è necessario (per il server)
var app = express();
var path = require('path');
var bodyParser = require("body-parser");
var TEMP_json = require('./template.json');     //Serve come template, ma non è quello aggiornato (che è "database.json")
var DB_json = require("./database.json");       //Questo è quello aggiornato
var fs = require('fs');
app.use(bodyParser.json());
//app.use(bodyParser.urlencoded({ extended: false }));    //Analizza il testo come dati codificati URL


//*********************POST REQUESTS****************************/
app.post("/", function(req,res){        //Questo gestisce le richieste POST
    //res.send('SERVER MESSAGE: Sto funzionando');
    console.log('------------------------------');
    
    DB_json = req.body; //Sovrascrivo la variabile con quello che ho ottenuto da POST
    var dataString = JSON.stringify(DB_json) //Converte in stringa DB_json
    fs.writeFile('database.json', dataString, (err) => {    //Lo salvo
        if (err) {throw err;}
        console.log("JSON data is saved.");
        });
        
    console.log("Ricevuto una richiesta POST");
    /* //console.log(req);
    console.log(req.body);              // contenuto della richiesta
    //console.log('Il tipo di dato è:', typeof req.body);
    //console.log('HEADERS -->', req.headers);
    console.log('Username:', req.body.username);     // username
    console.log('Password:', req.body.pass);         // password */
    console.log('------------------------------');
});

//*********************GET REQUESTS****************************/
app.get("/", function(req,res){         //Questo gestisce le richieste GET
    console.log('------------------------------');
    
    let rawdata = fs.readFileSync('database.json'); //Leggo i dati dal database
    let DB_json = JSON.parse(rawdata);              //Converto in JSON
    res.send(DB_json)                               //Invio la risposta con DB aggiornato

    console.log("Ricevuta una richiesta GET");
    /* console.log(req.body);
    //res.send(DB_json.Robot.Status.Is_Working);
    DB_json.Robot.Status.Task_Selected=DB_json.Robot.Status.Task_Selected+1;
    console.log(DB_json.Robot.Status.Task_Selected)
    var mexage = JSON.stringify(DB_json.Robot.Status.Task_Selected)
    //res.send(mexage) */
    console.log('------------------------------');
});

//*********************CREATING SERVER*************************/
var port = process.env.PORT || 5000;                //Creo un server sulla porta 5000
app.listen(port, function() {
    console.log("Listening on " + port);
    //DB_json.Robot.Status.Is_Working=true;
    //console.log(DB_json.Robot.Status)
});