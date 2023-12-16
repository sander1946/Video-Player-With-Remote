$.getJSON($SCRIPT_ROOT + '/_get_list',
function(data) {
var array = data.vuurwerk_info;

var div=document.createElement('div');
div.setAttribute('id','screen');

var input = document.createElement('input');
input.setAttribute('type', 'text');
input.setAttribute('id', 'CodeInput');
input.setAttribute('onkeyup', 'myFunction()');
input.setAttribute('placeholder', 'Zoek op naam of nummer');
input.setAttribute('title', 'Type een code');
div.appendChild(input)
var Currently_playing_wrapper = document.createElement("div");
Currently_playing_wrapper.setAttribute("id", "Currently_playing_wrapper")
div.appendChild(Currently_playing_wrapper)
var Currently_playing = document.createElement("div");
Currently_playing.setAttribute("id", "Currently_playing")
Currently_playing.innerText = "Volgende: "
Currently_playing_wrapper.appendChild(Currently_playing)

var ul=document.createElement('ul');
ul.setAttribute('id', 'myUL')


document.body.appendChild(div);
div.appendChild(ul);

for (var i=0; i<array.length; i++){

var li=document.createElement('li');
ul.appendChild(li);

var a=document.createElement('a');
li.appendChild(a);
var img=document.createElement('img');
a.appendChild(img)
img.src = array[i][2]
a.href = "javascript:sendCode(" + array[i][0] + ");";
a.setAttribute("onclick", "ChangeBackground(this);");
a.innerHTML = a.innerHTML + array[i][0] + " - " + array[i][1]
}
});
function myFunction() {
var input, filter, ul, li, a, i, txtValue;
input = document.getElementById("CodeInput");
filter = input.value.toUpperCase();
ul = document.getElementById("myUL");
li = ul.getElementsByTagName("li");
for (i = 0; i < li.length; i++) {
a = li[i].getElementsByTagName("a")[0];
txtValue = a.textContent || a.innerText;
if (txtValue.toUpperCase().indexOf(filter) > -1) {
li[i].style.display = "";
} else {
li[i].style.display = "none";
}
}
}
function sendCode(sCode) {
var request = new XMLHttpRequest();
var input = document.getElementById("CodeInput");
input.value = "";
myFunction();
request.open("POST", "/send_code");

request.setRequestHeader('Content-type', 'application/json');

var params = {
code: sCode
}

request.send(JSON.stringify(params));
}
function ChangeBackground(item) {
var el = document.getElementById("Currently_playing");
el.innerHTML = "<p>Volgende: </p>" + item.innerHTML;


item.classList.add("animating");

var listener = item.addEventListener('animationend', function() {
item.classList.remove("animating");

//this removes the listener after it runs so that it doesn't get re-added every time the button is clicked
item.removeEventListener('animationend', listener);
});
}
