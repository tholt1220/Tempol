// function updateSize() {
//   let nBytes = 0,
//       oFiles = this.files; //list of files (should be 1)
//   nBytes += oFiles[0].size; //number of bytes of first file
//   let sOutput = nBytes + " bytes";
//   // optional code for multiples approximation
//   const aMultiples = ["KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"];
//   for (nMultiple = 0, nApprox = nBytes / 1024; nApprox > 1; nApprox /= 1024, nMultiple++) {
//     sOutput = nApprox.toFixed(3) + " " + aMultiples[nMultiple];
//   }

//   // end of optional code
//   document.getElementById("fileSize").innerHTML = sOutput;
//   // updateTempo(oFiles[0]);
// }


function readFile(file)
{
  let reader = new FileReader();
  reader.readAsDataURL(file);
 
  reader.onload = function() {
    console.log(reader.result);
    var sound = new Audio(reader.result);
    //todo: export sound to file so it can be read by python script (currently is HTMLAudioElement)
  };

}
window.onload = function()
{
    toggle('n');    
    document.getElementById("fileButton").onclick = function() {toggle('f')};
    document.getElementById("ytButton").onclick = function() {toggle("y")};
}

function toggle(c) 
{
  var f_div = document.getElementById("file_div");
  var y_div = document.getElementById("youtube_div");

  if (c == 'f') //show file, hide youtube
  {
    f_div.style.display = "block";
    y_div.style.display = "none";
  }
  else if (c == 'y') //show youtube, hide file
  {
    f_div.style.display = "none";
    y_div.style.display = "block";
  }
  else //display neither
  {
    f_div.style.display = "none";
    y_div.style.display = "none";
  }

}


function deleteSong(id)
{
// DELETE
fetch('/playlistCRUD/' + id, {
  // Specify the method
  method: 'DELETE',

}).then(function (response) { //Song successfully deleted
  if(response.status = 200)
  {
    return response.text();
  }
  return response.text();
}).then(function (text) {

  console.log('DELETE response: ');

  // Should be 'OK' if everything was successful
  console.log(text);
  location.reload();
});
}

function duplicateSong(id)
{

// DELETE
fetch('/duplicateSong/' + id, {
  // Specify the method
  method: 'GET',

}).then(function (response) { //Song successfully deleted
  if(response.status = 200)
  {
    return response.text();
  }
  return response.text();
}).then(function (text) {

  console.log('GET response: ');

  // Should be 'OK' if everything was successful
  console.log(text);
  location.reload();
});
}


function songUp(trackNum)
{
  // var p = row.parentNode.parentNode; //Remove Row from table
  // p.parentNode.removeChild(p) 

// DELETE
fetch('/playlistUp/' + trackNum, {
  // Specify the method
  method: 'GET',

}).then(function (response) { //Song successfully deleted
  if(response.status = 200)
  {
    return response.text();
  }
  return response.text();
}).then(function (text) {

  console.log('DELETE response: ');

  // Should be 'OK' if everything was successful
  console.log(text);
  location.reload();
});
}

function loadAnimationFile()
{
  var e = document.getElementById("submit_buttonFile");
  e.style.display ="None";
  var p = e.parentNode;
  var img = document.createElement("img");
  img.src = "/static/loading.gif";
  img.className = "img-fluid";
  img.style.maxWidth = "20%";
  var txt = document.createTextNode("Okay, Calculating Tempo... (This might take a minute)");
  p.appendChild(txt);
  p.appendChild(img);
  disableClick();
}


function loadAnimationYT()
{
  var e = document.getElementById("submit_buttonYT");
  e.style.display ="None";
  var p = e.parentNode;
  var img = document.createElement("img");
  img.src = "/static/loading.gif";
  img.className = "img-fluid";
  img.style.maxWidth = "20%";

  var txt = document.createTextNode("Okay, Calculating Tempo... (This might take a minute)");
  p.appendChild(txt);
  p.appendChild(img);
  disableClick();
}

function loadAnimationConvert()
{
  var e = document.getElementById("submit_button");
  e.style.display ="None";
  var p = e.parentNode;
  var img = document.createElement("img");
  img.src = "/static/loading.gif";
  img.className = "img-fluid";
  img.style.maxWidth = "20%";

  var txt = document.createTextNode("Okay, Converting...");
  p.appendChild(txt);
  p.appendChild(img);
  disableClick();
}

function disableClick()
{
  var b = document.getElementsByTagName("BODY")[0];
  b.style.pointerEvents = "None";
}


// for Heroku, send timeouts if requests take longer than 30 secs
const extendTimeoutMiddleware = (req, res, next) => {
  const space = ' ';
  let isFinished = false;
  let isDataSent = false;

  // Only extend the timeout for API requests
  if (!req.url.includes('/upload')) {
    next();
    return;
  }

  res.once('finish', () => {
    isFinished = true;
  });

  res.once('end', () => {
    isFinished = true;
  });

  res.once('close', () => {
    isFinished = true;
  });

  res.on('data', (data) => {
    // Look for something other than our blank space to indicate that real
    // data is now being sent back to the client.
    if (data !== space) {
      isDataSent = true;
    }
  });

  const waitAndSend = () => {
    setTimeout(() => {
      // If the response hasn't finished and hasn't sent any data back....
      if (!isFinished && !isDataSent) {
        // Need to write the status code/headers if they haven't been sent yet.
        if (!res.headersSent) {
          res.writeHead(202);
        }

        res.write(space);

        // Wait another 15 seconds
        waitAndSend();
      }
    }, 15000);
  };

  waitAndSend();
  next();
};

app.use(extendTimeoutMiddleware);


