const media = document.getElementById("contents")
var occurrence = JSON.parse(document.getElementById("medium_info").textContent);
var shiftHold = false

for ([object_id, medium_info] of Object.entries(occurrence)) {
    var newMedium = document.createElement("div")
    var textDiv = document.createElement("div")
    var newInput = document.createElement("input")

    newInput.setAttribute("class", "form-check-input ms-3")
    newInput.setAttribute("type", "checkbox")
    textDiv.setAttribute("class", "ms-5")

    newMedium.setAttribute("id", object_id)
    newMedium.setAttribute("class", "my-2 border border-secondary rounded d-flex align-items-center")
    newMedium.style.border = "thick solid #0000FF"
    medium_info["individual"].forEach(function (element) {
        var newPara = document.createElement("p")
        var newText = document.createTextNode(element)
        newPara.appendChild(newText)
        textDiv.appendChild(newPara)
    });
    newMedium.appendChild(newInput)
    newMedium.appendChild(textDiv)
    media.appendChild(newMedium)
}

document.addEventListener("keydown", function (event) {
    if (event.code === "ShiftRight" || event.code === "ShiftLeft") {
        var shiftHold = true
        console.log(shiftHold)
    }
})

document.addEventListener("keyup", function (event) {
    if (event.code === "ShiftRight" || event.code === "ShiftLeft") {
        var shiftHold = false
        console.log(shiftHold)
    }
})

document.addEventListener("click", function (event) {
    if (shiftHold) {

    } else {
        let clickMedium = event.target
        console.log(clickMedium.id)
    }
})



// var r = new XMLHttpRequest();
// r.open("POST", "/_species_prediction", true);
// r.onreadystatechange = function () {
//     if (r.readyState != 4 || r.status != 200) return;
//     alert("Success: " + r.responseText);
// };
// r.send("banana=yellow");

// var content = document.getElementById("contents")





