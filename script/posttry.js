//import axios from 'axios';
const axios = require("axios");
// const fetch = require ('node-fetch');
//const { json } = require("body-parser");
var DB2_json = require('./template.json')
var fs = require('fs');

//devo capire come scrivere il formato dei dati 
/* const pload = JSON.stringify({
    'username': 'UR10',
    'pass': 'ScrivoDaJS'})
 */
  /* const pload = {
    username: 'UR10',
    pass: 'ScrivoDaJS'
  } */

  pload = {'username':'UR10','pass':'Javascript'}
  /* var username = 'UR10';
  var pass = 'Javascript'
  const pload = {username, pass}; */

  console.log('Il dato è:', pload);
  //console.log('Il tipo di dato è:', typeof pload);
  console.log(pload.username);
  console.log(pload.pass);

    
  ///////////////AXIOS//////////////////////
  axios.post(`http://localhost:5000/`, pload)    //Qui posso mettere sia localhost che il link di ngrok
    .then(res => {
      //console.log(res);
      console.log(res.data);
    })

 /* axios.get('http://localhost:5000/')
    .then(res => {
      console.log(res.data);
    })*/
  //////////////////////////////////////////

  console.log(DB2_json.Robot.Status)

  ///////////////////SCRIVERE SU JSON/////////////////////////
  
  var JSONmodified = require('./WritingTEST.json')  //Crea una variabile prendendo il file che poi modifico
  console.log(DB2_json.Robot.Status.Is_Working) //Qui il valore non è ancora modificato (= false)

  DB2_json.Robot.Status.Is_Working=true;        //Qui modifico il valore (= true)

  var dataString = JSON.stringify(DB2_json)     //Lo converto in stringa per salvarlo con writeFile
  fs.writeFile('WritingTEST.json', dataString, (err) => {    //Lo salvo
    if (err) {
        throw err;
    }
    console.log("JSON data is saved.");
    var JSONmodified = require('./WritingTEST.json')         //Qui in realtà prende il file prima delle modifiche
    //Devo provare a usare Async/Await
    console.log(JSONmodified.Robot.Status.Is_Working)     //Qui invece il valore non è modificato (=false)
});
