document.addEventListener("DOMContentLoaded", () => {
    var occurrences = JSON.parse(document.getElementById("occurrence_info").textContent);
    var occurrencesDiv = document.getElementById("occurrences_container")
    var occurrenceTemplate = document.getElementById("occurrence_template").cloneNode(true)
    var individualTemplate = document.getElementById("individual").cloneNode(true)
    var pmModal = document.getElementById("pm-modal")
    const closePmModal = document.getElementById("close-pm-modal")
    occurrenceTemplate.getElementsByTagName("tbody")[0].innerHTML = ""
    occurrencesDiv.innerHTML = ""

    for (const [object_id, medium] of Object.entries(occurrences)) {
        var occurrence = occurrenceTemplate.cloneNode(true)
        occurrence.id = object_id

        var individualContainer = occurrence.getElementsByTagName("tbody")[0]


        for (var individual of medium["individual"]) {
            var newIndividual = individualTemplate.cloneNode(true)
            newIndividual.getElementsByClassName("ai_species")[0].innerHTML = individual["chinese_common_name_ai"]
            newIndividual.querySelector("input[name='xmax']").value = individual["xmax"]
            newIndividual.querySelector("input[name='xmin']").value = individual["xmin"]
            newIndividual.querySelector("input[name='ymax']").value = individual["ymax"]
            newIndividual.querySelector("input[name='ymin']").value = individual["ymin"]

            individualContainer.appendChild(newIndividual)
        }

        occurrencesDiv.appendChild(occurrence)
    }

    var pmOccurrences = document.getElementsByClassName("pm-occurrence")
    for (var pmOccurrence of pmOccurrences) {
        var img = pmOccurrence.getElementsByTagName("img")[0]
        var url = occurrences[pmOccurrence.id]["path"].replaceAll("\\", "/").replaceAll("#", "%23").substring(2)
        img.src = `/uploads/${url}`
    }

    setHeartCheck()
    setSpeciessearch()
    setImageModalTrigger()


    function setHeartCheck() {
        var hearts = document.getElementsByClassName("pm-heart")
        for (let i = 0; i < hearts.length; i++) {
            hearts[i].addEventListener("click", clickFeature)
        }
    }

    function clickFeature(event) {
        var heart = event.target
        var neighborCheckBox = heart.parentElement.getElementsByTagName("input")[0]
        neighborCheckBox.checked = !neighborCheckBox.checked
        if (neighborCheckBox.checked) {
            heart.classList.remove("text-secondary")
            heart.classList.add("text-danger")
            heart.classList.add("border-4")
        } else {
            heart.classList.add("text-secondary")
            heart.classList.remove("text-danger")
            heart.classList.remove("border-4")

        }
    }


    function setSpeciessearch() {
        var commonChNameInput = document.getElementsByName("common_ch_name")
        for (let i = 0; i < commonChNameInput.length; i++) {
            commonChNameInput[i].addEventListener("input", searchSpecies)
        }
    }

    function searchSpecies(event) {

        // datalist.textContent = ""
        var xhr = new XMLHttpRequest()
        xhr.open("post", "/species_input_predict", true)
        xhr.send(event.target.value)
        xhr.onload = function () {
            if (xhr.status == 200) {
                var predictions = JSON.parse(xhr.responseText)
                var speciesList = []
                for (let p of predictions) {
                    speciesList.push({ label: p[1], value: p[1] })
                    console.log(p[1], p[0])
                }
                $(".pm-review-species").autocomplete({
                    minLength: 0,
                    source: function (request, response) {
                        response(speciesList)
                    }
                })
            }
        }
    }


    function setImageModalTrigger() {
        var images = document.getElementsByClassName("pm-image")
        for (var image of images) {
            image.addEventListener("click", clickImage)
        }
    }

    function clickImage(event) {
        var object_id = event.target.parentElement.parentElement.id
        pmModal.style.display = "block"
        modalInfo = {
            "src": event.target.src
        }
        setModalContent(modalInfo)
    }

    function setModalContent(modalInfo) {
        document.getElementById("pm-modal-image").src = modalInfo["src"]
    }

    function showOccurrenceModal() {

    }

    pmModal.addEventListener("click", function (event) {
        if (event.target.id == pmModal.id) {
            this.style.display = "none"
        }
    })

    closePmModal.addEventListener("click", function (event) {
        pmModal.style.display = "none"
    })




})