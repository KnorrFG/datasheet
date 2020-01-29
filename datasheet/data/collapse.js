String.prototype.replaceAt=function(index, replacement) {
    return this.substr(0, index) + replacement +
	this.substr(index + replacement.length);
}

var coll = document.getElementsByClassName("hdr");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    var content = this.nextElementSibling;
    if (content.style.display == "none"){
	content.style.display = "block";
	this.innerText = this.innerText.replaceAt(0, "\u2798")
    } else {
	content.style.display = "none";
	this.innerText = this.innerText.replaceAt(0, "\u2799")
    }
  });
}
