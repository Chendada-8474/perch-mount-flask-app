var mediaDiv = document.getElementById("media_container")
var falseNegativeDiv = document.getElementById("fn_container")
var rawMedia = JSON.parse(document.getElementById("medium_info").textContent);
var mediumTemplate = document.getElementById("medium_template").cloneNode(true)
mediumTemplate.removeAttribute("id")

var contentsDiv = document.getElementById("contents")

var imgSizeRange = document.getElementById("img_size_range")
var savePreffence = document.getElementById("save_preffence")

var clearSelection = document.getElementById("clear_selection")
var addToFalseNegative = document.getElementById("add_to_false_negative")
var cancelChecked = document.getElementById("cancel_checked")

var numChecked = document.getElementById("num_checked")

var lastCheckId = null
document.getElementById("medium_template").remove();


document.addEventListener("DOMContentLoaded", () => {
    var media = mediaDiv.getElementsByClassName("pm-media")

    if (getCookieByName("empty_check_img_size")) {
        var img_size = getCookieByName("empty_check_img_size");
    } else {
        var img_size = "20rem"
    }

    for (var i = 0; i < rawMedia.length; i++) {
        var new_medium = mediumTemplate.cloneNode(true)
        var medium_index = new_medium.getElementsByTagName("p")[0]

        new_medium.setAttribute("id", rawMedia[i]["object_id"])
        new_medium.style.width = img_size;
        medium_index.innerText = `${i + 1}/${rawMedia.length}`
        mediaDiv.appendChild(new_medium)
    }

    for (var i = 0; i < media.length; i++) {
        // var url = rawMedia[i]["path"].replaceAll("\\", "/").replaceAll("#", "%23").substring(2)
        var url = rawMedia[i]["path"]
        let s = url.split(".")
        var ext = s[s.length - 1].toLowerCase()
        if (ext == "jpg" || ext == "jpeg") {
            var img = media[i].querySelector("img")
            var video = media[i].querySelector("video")
            img.addEventListener("click", mediumClick)
            img.src = `/uploads/${url}`
            video.remove()
        } else {
            var img = media[i].querySelector("img")
            var video = media[i].querySelector("video")
            video.addEventListener("click", mediumClick)
            video.src = `/uploads/${url}`
            img.remove()
        }
    }

    function mediumClick(event) {

        var medium = event.target.parentElement
        var mediumInput = medium.querySelector("input[name='temp_select']")
        var checkState = mediumInput.checked
        mediumInput.checked = !checkState
        if (event.shiftKey && mediumInput.checked) {
            if (mediumInput.checked) {
                shiftSelect(document.lastCheckId, medium.id)
            }
        } else {
            changeStateChange(medium, mediumInput.checked)
            if (mediumInput.checked) {
                document.lastCheckId = medium.id
            }
        }
    }

    contentsDiv.addEventListener("click", function (event) {
        if (event.target.id == "media_container") {
            for (var i = 0; i < media.length; i++) {
                var mediumInput = media[i].querySelector("input[name='temp_select']")
                mediumInput.checked = false
                changeStateChange(media[i], false)
            }
        }
    })

    clearSelection.addEventListener("click", function (event) {
        for (var i = 0; i < media.length; i++) {
            var mediumInput = media[i].querySelector("input[name='temp_select']")
            mediumInput.checked = false
            changeStateChange(media[i], false)
        }
    })

    falseNegativeDiv.addEventListener("click", function (event) {
        if (event.target.id == "fn_container") {
            var falseNagetiveMedia = falseNegativeDiv.getElementsByClassName("pm-media")
            for (var i = 0; i < falseNagetiveMedia.length; i++) {
                var mediumInput = falseNagetiveMedia[i].querySelector("input[name='temp_select']")
                mediumInput.checked = false
                changeStateChange(falseNagetiveMedia[i], false)
            }
        }
    })

    savePreffence.addEventListener("click", function (event) {
        var imgSize = imgSizeRange.value
        document.cookie = `empty_check_img_size=${imgSize}rem`
        for (var i = 0; i < media.length; i++) {
            media[i].style.width = `${imgSize}rem`
        }
    })

    addToFalseNegative.addEventListener("click", function (event) {
        var moveIds = []
        for (var i = 0; i < media.length; i++) {
            var mediumInput = media[i].querySelector("input[name='temp_select']")
            if (mediumInput.checked) {
                moveIds.push(media[i].id)
            }
        }
        for (mediumId of moveIds) {
            moveMediaToFN(mediumId)
        }
        numChecked.innerText = falseNegativeDiv.childElementCount
    })

    cancelChecked.addEventListener("click", function (event) {
        var moveIds = []
        var fnMedia = falseNegativeDiv.children
        for (var i = 0; i < fnMedia.length; i++) {
            var checked = fnMedia[i].querySelector("input[name='temp_select']").checked
            if (checked) {
                moveIds.push(fnMedia[i].id)
            }
        }
        for (mediumId of moveIds) {
            moveBackMedia(mediumId)
        }
        numChecked.innerText = falseNegativeDiv.childElementCount
    })

    for (let bt of document.getElementsByClassName("back-to-top")) {
        bt.addEventListener("click", event => {
            window.scrollTo(0, 0)
        })
    }

})

function shiftSelect(lastCheckId, shiftSelectId) {
    var select = false
    var media = mediaDiv.getElementsByClassName("pm-media")
    for (var medium of media) {
        var mediumInput = medium.querySelector("input[name='temp_select']")
        if (medium.id == lastCheckId || medium.id == shiftSelectId) {
            var select = !select
        }
        if (select || medium.id == lastCheckId || medium.id == shiftSelectId) {
            mediumInput.checked = true
            changeStateChange(medium, true)
        } else {
            mediumInput.checked = false
            changeStateChange(medium, false)
        }
    }
}


function changeStateChange(medium, checked) {
    if (checked) {
        medium.classList.remove("border-0")
        medium.classList.add("border-3")
        medium.classList.add("opacity-50")
    } else {
        medium.classList.add("border-0")
        medium.classList.remove("border-3")
        medium.classList.remove("opacity-50")
    }
}

function moveMediaToFN(mediaId) {
    var moveMedium = document.getElementById(mediaId)
    falseNegativeDiv.prepend(moveMedium)
    moveMedium.style.width = "15rem"
    moveMedium.querySelector("input[name='temp_select']").checked = false
    changeStateChange(moveMedium, false)
}

function moveBackMedia(mediaId) {
    var moveMedium = document.getElementById(mediaId)
    mediaDiv.prepend(moveMedium)
    moveMedium.style.width = `${imgSizeRange.value}rem`
    moveMedium.querySelector("input[name='temp_select']").checked = false
    changeStateChange(moveMedium, false)
}

function send_check_data() {
    var falseNagetiveIds = new Set()
    var emptyIds = []
    var notEmptyRawMedia = []
    for (medium of falseNegativeDiv.children) {
        falseNagetiveIds.add(medium.id)
    }
    for (medium of mediaDiv.children) {
        emptyIds.push(medium.id)
    }
    for (var i = 0; i < rawMedia.length; i++) {
        if (falseNagetiveIds.has(rawMedia[i]["object_id"])) {
            delete rawMedia[i].path
            delete rawMedia[i].detected_date
            delete rawMedia[i].file_issue
            notEmptyRawMedia.push(rawMedia[i])
        }
    }

    data = { "fn_object_data": notEmptyRawMedia, "empty_object_id": emptyIds }
    document.getElementById("send").value = JSON.stringify(data)
}


function getCookieByName(name) {
    return document.cookie
        .split("; ")
        .find((row) => row.startsWith(`${name}=`))
        ?.split("=")[1];
}