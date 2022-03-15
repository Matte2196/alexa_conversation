//import axios from 'axios';
const axios = require("axios");
// const fetch = require ('node-fetch');
//const { json } = require("body-parser");

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