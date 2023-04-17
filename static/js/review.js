var occurrences = JSON.parse(document.getElementById("occurrence_info").textContent);

document.addEventListener("DOMContentLoaded", () => {
    var occurrencesDiv = document.getElementById("occurrences_container")
    var occurrenceTemplate = document.getElementById("occurrence_template").cloneNode(true)
    var individualTemplate = document.getElementById("individual").cloneNode(true)

    var pmModal = document.getElementById("pm-modal")
    const closePmModal = document.getElementById("close-pm-modal")
    var boundingBoxPainter = document.getElementById("bounding-box-painter")
    var boundingBoxes = document.getElementById("bounding-boxes")
    var pointerX = document.getElementById("pointer-x")
    var pointerY = document.getElementById("pointer-y")
    var newBoundingBox = document.createElement("div")
    var horizontalLine = document.getElementById("horizontal")
    var verticalLine = document.getElementById("vertical")
    var modalIndividualTemplate = document.getElementById("modal-individual-template").cloneNode(true)
    var modalIndividualContainer = document.getElementById("modal-individual-container")
    const backMedium = document.getElementById("back-medium")
    const nextMedium = document.getElementById("next-medium")

    const newBoxesClasses = ["position-absolute", "rounded"]
    const boxColors = ["#C7C7E2", "#D2A2CC", "#A3D1D1", "#CDCD9A", "#D9B3B3", "#FFED97", "#A6FFA6", "#FF95CA", "#D0D0D0", "#CA8EFF", "#D3FF93"]
    const newBoxColors = ["#a6d7de", "#83f0bb", "#7281cf", "#3f8f2e", "#dee022", "#d25af9", "#e89860", "#97f6c5", "#d769c5", "#bfd04a", "#9cd682"]
    var newIndividualBeginId = 20000
    var newBoxColorIndex = 0
    var boundingBoxMouseDown = false
    var currentModalId = null

    var mediumCheckBoxes = document.getElementsByClassName("pm-medium-selected")
    var lastCheckMediumId = null

    const confirmEdition = document.getElementById("confirm-edit")
    var speciesEdit = document.getElementById("edit-species")
    var mainBehaviorEdit = document.getElementById("edit-main-behavior")
    var secondaryBehaviorEdit = document.getElementById("edit-secondary-behavior")
    var preyEdit = document.getElementById("edit-prey")
    var adultEdit = document.getElementById("edit-adult")
    var taggedEdit = document.getElementById("edit-tagged")
    var transmitterEdit = document.getElementById("edit-transmitter")


    occurrenceTemplate.getElementsByTagName("tbody")[0].innerHTML = ""
    occurrencesDiv.innerHTML = ""

    for (const [object_id, medium] of Object.entries(occurrences)) {
        var occurrence = occurrenceTemplate.cloneNode(true)
        occurrence.id = object_id

        var individualContainer = occurrence.getElementsByTagName("tbody")[0]

        var individualIndex = 0
        for (var individual of medium["individual"]) {
            var newIndividual = individualTemplate.cloneNode(true)
            newIndividual.getElementsByClassName("ai_species")[0].innerHTML = individual["chinese_common_name_ai"]
            newIndividual.querySelector("input[name='xmax']").value = individual["xmax"]
            newIndividual.querySelector("input[name='xmin']").value = individual["xmin"]
            newIndividual.querySelector("input[name='ymax']").value = individual["ymax"]
            newIndividual.querySelector("input[name='ymin']").value = individual["ymin"]
            newIndividual.id = `${object_id}-${individualIndex}`
            individualContainer.appendChild(newIndividual)
            individualIndex++
        }

        occurrencesDiv.appendChild(occurrence)
    }

    var pmOccurrences = document.getElementsByClassName("pm-occurrence")
    for (var pmOccurrence of pmOccurrences) {
        var img = pmOccurrence.getElementsByTagName("img")[0]
        var url = occurrences[pmOccurrence.id]["path"].replaceAll("\\", "/").replaceAll("#", "%23").substring(2)
        img.src = `/uploads/${url}`
        var baseName = url.split("/")
        var fileNameSmall = pmOccurrence.querySelector("small")
        fileNameSmall.innerHTML = baseName[baseName.length - 1]
    }

    setHeartCheck()
    setSpeciessearch()
    setImageModalTrigger()
    setMediumCheckBoxes()

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
        speciesEdit.addEventListener("input", searchSpecies)
    }

    function searchSpecies(event) {
        var xhr = new XMLHttpRequest()
        xhr.open("post", "/species_input_predict", true)
        xhr.send(event.target.value)
        xhr.onload = function () {
            if (xhr.status == 200) {
                var predictions = JSON.parse(xhr.responseText)
                var speciesList = []
                for (let p of predictions) {
                    speciesList.push({ label: p[1], value: p[1] })
                }
                $(event.target).autocomplete({
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
        currentModalId = event.target.parentElement.parentElement.parentElement.id
        pmModal.style.display = "block"
        document.getElementById("current-modal-object-id").value = currentModalId
        var individuals = document.getElementById(currentModalId).getElementsByTagName("tbody")[0]
        modalInfoIndividuals = []
        for (var indi of individuals.children) {
            modalInfoIndividuals.push({
                "individual_id": indi.id,
                "chinese_common_name_ai": indi.getElementsByClassName("ai_species")[0].innerHTML,
                "chinese_common_name_human": indi.querySelector("input[name='common_ch_name']").value,
                "xmax": indi.querySelector("input[name='xmax']").value,
                "xmin": indi.querySelector("input[name='xmin']").value,
                "ymax": indi.querySelector("input[name='ymax']").value,
                "ymin": indi.querySelector("input[name='ymin']").value,
            })
        }

        modalInfo = {
            "src": event.target.src,
            "individuals": modalInfoIndividuals,
        }
        setModalContent(modalInfo)
    }

    function setModalContent(modalInfo) {
        var image = document.getElementById("pm-modal-image")
        image.src = modalInfo["src"]
        imageWidth = image.offsetWidth
        imageHeight = image.offsetHeight
        boundingBoxPainter.style.width = `${imageWidth}px`
        boundingBoxPainter.style.height = `${imageHeight}px`
        boundingBoxes.style.width = `${imageWidth}px`
        boundingBoxes.style.height = `${imageHeight}px`
        boundingBoxes.innerHTML = ""

        modalIndividualContainer.innerHTML = ""
        modalIndividualContainer.addEventListener("focusout", (event) => {
            var modalIndividualId = event.target.parentElement.parentElement.id
            let phrases = modalIndividualId.split("-")
            document.getElementById(`${phrases[1]}-${phrases[2]}`).querySelector("input[name='common_ch_name']").value = event.target.value
        })

        var colorIndex = 0
        newBoxColorIndex = 0
        for (individual of modalInfo["individuals"]) {
            if (colorIndex > boxColors.length) {
                colorCode = "#" + Math.floor(Math.random() * 16777215).toString(16)
            } else {
                colorCode = boxColors[colorIndex]
                colorIndex++
            }

            var newModalIndividual = createModalIndividual(individual, colorCode)
            modalIndividualContainer.appendChild(newModalIndividual)

            var top = Math.round(image.offsetHeight * individual["ymin"])
            var start = Math.round(image.offsetWidth * individual["xmin"])
            var cloneBoundingBox = document.createElement("div")

            cloneBoundingBox.id = "box-" + individual["individual_id"]
            cloneBoundingBox.style.border = "solid"
            cloneBoundingBox.style.borderWidth = "5px"
            cloneBoundingBox.style.borderColor = colorCode
            for (c of newBoxesClasses) {
                cloneBoundingBox.classList.add(c)
            }
            cloneBoundingBox.style.top = `${top}px`
            cloneBoundingBox.style.left = `${start}px`
            cloneBoundingBox.style.height = `${Math.round(image.offsetHeight * individual["ymax"]) - top}px`
            cloneBoundingBox.style.width = `${Math.round(image.offsetWidth * individual["xmax"]) - start}px`

            var speciesName = document.createElement("span")
            speciesName.style.backgroundColor = colorCode
            speciesName.classList.add("d-inline")
            speciesName.classList.add("p-1")
            speciesName.classList.add("text-white")
            speciesName.classList.add("rounded")

            if (individual["chinese_common_name_human"]) {
                speciesName.innerHTML = individual["chinese_common_name_human"]
            } else {
                speciesName.innerHTML = individual["chinese_common_name_ai"]
            }
            cloneBoundingBox.appendChild(speciesName)

            boundingBoxes.appendChild(cloneBoundingBox)

        }
    }


    function createModalIndividual(individual, colorCode) {
        var newModalIndividual = modalIndividualTemplate.cloneNode(true)
        var modalInputSpecies = newModalIndividual.getElementsByClassName("human-species")[0]
        modalInputSpecies.addEventListener("input", searchSpecies)

        newModalIndividual.getElementsByClassName("delete-individual")[0].addEventListener("click", deleteIndividual)
        newModalIndividual.style.background = colorCode
        newModalIndividual.id = "modal-" + individual["individual_id"]
        newModalIndividual.getElementsByClassName("ai-species")[0].innerHTML = individual["chinese_common_name_ai"]
        modalInputSpecies.value = individual["chinese_common_name_human"]
        newModalIndividual.getElementsByClassName("xmax")[0].innerHTML = individual["xmax"]
        newModalIndividual.getElementsByClassName("xmin")[0].innerHTML = individual["xmin"]
        newModalIndividual.getElementsByClassName("ymax")[0].innerHTML = individual["ymax"]
        newModalIndividual.getElementsByClassName("ymin")[0].innerHTML = individual["ymin"]
        return newModalIndividual
    }


    function deleteIndividual(event) {
        var modalIndividualId = event.target.parentElement.parentElement.id

        let phrases = modalIndividualId.split("-")
        var boxIndividualId = `box-${phrases[1]}-${phrases[2]}`
        var individualId = `${phrases[1]}-${phrases[2]}`

        document.getElementById(boxIndividualId).remove()
        document.getElementById(individualId).remove()
        document.getElementById(modalIndividualId).remove()
    }


    boundingBoxPainter.addEventListener("mousemove", (event) => {
        let originX = event.target.getBoundingClientRect().left
        let originY = event.target.getBoundingClientRect().top
        pointerX.innerHTML = ((event.clientX - originX) / event.target.offsetWidth).toFixed(4)
        pointerY.innerHTML = ((event.clientY - originY) / event.target.offsetHeight).toFixed(4)
        if (boundingBoxMouseDown) {
            let w = event.clientX - newBoundingBox.getBoundingClientRect().left
            let h = event.clientY - newBoundingBox.getBoundingClientRect().top
            newBoundingBox.style.width = `${w}px`
            newBoundingBox.style.height = `${h}px`
        }

        horizontalLine.style.width = `${event.target.offsetWidth}px`
        horizontalLine.style.height = `${event.clientY - originY}px`
        verticalLine.style.width = `${event.clientX - originX}px`
        verticalLine.style.height = `${event.target.offsetHeight}px`
    });


    boundingBoxPainter.addEventListener("mousedown", (event) => {
        let currentModalId = document.getElementById("current-modal-object-id").value
        let originX = event.target.getBoundingClientRect().left
        let originY = event.target.getBoundingClientRect().top
        let colorCode = newBoxColors[newBoxColorIndex]
        newBoundingBox = document.createElement("div")
        newBoundingBox.id = `box-${currentModalId}-${newIndividualBeginId}`
        newBoundingBox.style.border = "solid"
        newBoundingBox.style.borderWidth = "4px"
        newBoundingBox.style.borderColor = colorCode
        newBoundingBox.style.left = `${event.clientX - originX}px`
        newBoundingBox.style.top = `${event.clientY - originY}px`
        for (c of newBoxesClasses) {
            newBoundingBox.classList.add(c)
        }
        boundingBoxes.appendChild(newBoundingBox)
        boundingBoxMouseDown = true
    })

    boundingBoxPainter.addEventListener("mouseup", function (event) {
        boundingBoxMouseDown = false
        var boxContainerRect = newBoundingBox.parentElement.getBoundingClientRect()
        var boxRect = newBoundingBox.getBoundingClientRect()
        if (boxRect.width < 50 && boxRect.height < 50) {
            newBoundingBox.remove()
        } else {
            let currentModalId = document.getElementById("current-modal-object-id").value
            let colorCode = newBoxColors[newBoxColorIndex]
            let individual = {
                "individual_id": `${currentModalId}-${newIndividualBeginId}`,
                "chinese_common_name_ai": "",
                "chinese_common_name_human": "",
                "xmax": ((boxRect.right - boxContainerRect.left) / boxContainerRect.width).toFixed(4),
                "xmin": ((boxRect.left - boxContainerRect.left) / boxContainerRect.width).toFixed(4),
                "ymax": ((boxRect.bottom - boxContainerRect.top) / boxContainerRect.height).toFixed(4),
                "ymin": ((boxRect.top - boxContainerRect.top) / boxContainerRect.height).toFixed(4),
            }
            var newModalIndividual = createModalIndividual(individual, colorCode)
            modalIndividualContainer.append(newModalIndividual)

            var individualContainer = document.getElementById(currentModalId).getElementsByTagName("tbody")[0]
            var newIndividual = individualTemplate.cloneNode(true)

            newIndividual.getElementsByClassName("ai_species")[0].innerHTML = individual["chinese_common_name_ai"]
            newIndividual.querySelector("input[name='common_ch_name']").addEventListener("input", searchSpecies)
            newIndividual.querySelector("input[name='xmax']").value = individual["xmax"]
            newIndividual.querySelector("input[name='xmin']").value = individual["xmin"]
            newIndividual.querySelector("input[name='ymax']").value = individual["ymax"]
            newIndividual.querySelector("input[name='ymin']").value = individual["ymin"]
            newIndividual.id = `${currentModalId}-${newIndividualBeginId}`
            individualContainer.appendChild(newIndividual)
            newIndividualBeginId++
            newBoxColorIndex++
        }
    })


    pmModal.addEventListener("click", function (event) {
        if (event.target.id == pmModal.id) {
            this.style.display = "none"
        }
    })

    closePmModal.addEventListener("click", function (event) {
        pmModal.style.display = "none"
    })


    // backMedium.addEventListener("click", (event) => {
    //     var currentModalId = document.getElementById("current-modal-object-id").value

    //     var backId = document.getElementById(currentModalId).previousSibling.id
    //     currentModalId.value = backId

    //     var individuals = document.getElementById(currentModalId).getElementsByTagName("tbody")[0]
    //     modalInfoIndividuals = []
    //     for (var indi of individuals.children) {
    //         modalInfoIndividuals.push({
    //             "individual_id": indi.id,
    //             "chinese_common_name_ai": indi.getElementsByClassName("ai_species")[0].innerHTML,
    //             "chinese_common_name_human": indi.querySelector("input[name='common_ch_name']").value,
    //             "xmax": indi.querySelector("input[name='xmax']").value,
    //             "xmin": indi.querySelector("input[name='xmin']").value,
    //             "ymax": indi.querySelector("input[name='ymax']").value,
    //             "ymin": indi.querySelector("input[name='ymin']").value,
    //         })
    //     }

    //     modalInfo = {
    //         "src": document.getElementById(backId).querySelector("img").src,
    //         "individuals": modalInfoIndividuals,
    //     }
    //     setModalContent(modalInfo)

    // })

    // nextMedium.addEventListener("click", (event) => {
    //     var currentModalId = document.getElementById("current-modal-object-id").value
    //     var nextId = document.getElementById(currentModalId).nextSibling.id
    //     console.log(nextId)
    // })



    function setMediumCheckBoxes() {
        for (checkBox of mediumCheckBoxes) {
            checkBox.addEventListener("click", mediumCheckBoxesChanged)
        }
    }


    function mediumCheckBoxesChanged(event) {
        if (event.shiftKey && event.target.checked) {
            shiftSelect(document.lastCheckMediumId, event.target.parentElement.id)
        } else if (event.target.checked) {
            changeMediumCheckedStyle(event.target.parentElement, event.target.checked)
            document.lastCheckMediumId = event.target.parentElement.id
        }
    }

    function shiftSelect(lastCheckId, shiftSelectId) {
        var select = false
        for (var medium of pmOccurrences) {
            var mediumInput = medium.querySelector("input[name='temp-select']")
            if (medium.id == lastCheckId || medium.id == shiftSelectId) {
                var select = !select
            }
            if (select || medium.id == lastCheckId || medium.id == shiftSelectId) {
                mediumInput.checked = true
                changeMediumCheckedStyle(medium, true)
            } else {
                mediumInput.checked = false
                changeMediumCheckedStyle(medium, false)
            }
        }
    }

    function changeMediumCheckedStyle(medium, checked) {
        if (checked) {
            medium.classList.remove("border-0")
            medium.classList.add("border-3")
        } else {
            medium.classList.add("border-0")
            medium.classList.remove("border-3")
        }
    }

    occurrencesDiv.parentElement.parentElement.addEventListener("click", function (event) {
        if (event.target.tagName != "INPUT" || event.target.name != "temp-select") {
            for (var medium of pmOccurrences) {
                var mediumInput = medium.querySelector("input[name='temp-select']")
                mediumInput.checked = false
                changeMediumCheckedStyle(medium, false)
            }
        }
    })

    confirmEdition.addEventListener("click", function (event) {
        for (var medium of pmOccurrences) {
            if (medium.querySelector("input[name='temp-select']").checked) {
                var individuals = medium.querySelectorAll("tbody > tr")
                for (var indi of individuals) {
                    indi.querySelector("input[name='common_ch_name']").value = speciesEdit.value
                    indi.querySelector("select[name='main_behavior']").value = mainBehaviorEdit.value
                    indi.querySelector("select[name='secondary_behavior']").value = secondaryBehaviorEdit.value
                    indi.querySelector("input[name='prey']").checked = preyEdit.checked
                    indi.querySelector("input[name='adult']").checked = adultEdit.checked
                    indi.querySelector("input[name='tagged']").checked = taggedEdit.checked
                    indi.querySelector("input[name='transmitter']").checked = transmitterEdit.checked
                }
            }
        }
    })


    document.getElementById("open-confirm-modal").addEventListener("click", checkSpecies)

    function checkSpecies(event) {
        var commonNames = []
        for (medium of occurrencesDiv.children) {
            var fileName = medium.querySelector("small").innerHTML
            var names = []
            var mediumCommonNames = medium.querySelectorAll("input[name='common_ch_name']")
            for (var commonName of mediumCommonNames) {
                names.push(commonName.value)
            }
            commonNames.push(
                {
                    "file_name": fileName,
                    "chinese_common_name": names
                }
            )
        }
        var confirmModalBody = document.getElementById("confirm-model-body")
        var invalidMedia = []
        var xhr = new XMLHttpRequest()
        xhr.open("post", "/check_common_name", true)
        xhr.setRequestHeader('Content-Type', 'application/json')
        xhr.send(JSON.stringify(commonNames))
        xhr.onload = function () {
            if (xhr.status != 200) {
                return
            }
            var results = JSON.parse(xhr.responseText)
            for (var result of results) {
                if (!result["valid"]) {
                    invalidMedia.push(result["file_name"])
                }
            }
            var confirmSendButton = document.getElementById("confirm-send-button")
            if (invalidMedia.length != 0) {
                confirmSendButton.disabled = true
                confirmModalBody.innerHTML = ""
                var alertDiv = document.createElement("div")
                for (var invalidMedium of invalidMedia) {
                    var issueP = document.createElement("p")
                    issueP.innerHTML = invalidMedium
                    alertDiv.appendChild(issueP)
                }
                var issueP = document.createElement("p")
                issueP.innerHTML = "以上檔案輸入物種有誤，請確認"
                alertDiv.appendChild(issueP)
                alertDiv.classList.add("alert")
                alertDiv.classList.add("alert-warning")
                confirmModalBody.append(alertDiv)
            } else {
                confirmSendButton.disabled = false
                confirmModalBody.innerHTML = "確認要送出了嗎？此動作會直接更該資料庫的內容，請完全確認檢查完畢後再送出。"
            }
        }
    }

})


function send_review() {
    confirmedData = []
    emptyObjectIds = []
    var occurrencesDiv = document.getElementById("occurrences_container")
    for (var medium of occurrencesDiv.children) {
        var object_id = medium.id
        var featured = medium.querySelector("input[name='featured']").checked
        var individuals = medium.querySelector("tbody").children
        if (individuals.length == 0) {
            emptyObjectIds.push(object_id)
        }
        for (var individual of individuals) {
            var chinese_common_name_by_ai = individual.querySelector("td[class='ai_species']").innerHTML
            var chinese_common_name_by_human = individual.querySelector("input[name='common_ch_name']").value
            if (!chinese_common_name_by_human) {
                chinese_common_name_by_human = chinese_common_name_by_ai
            }
            var main_behavior = individual.querySelector("select[name='main_behavior']").value
            var secondary_behavior = individual.querySelector("select[name='secondary_behavior']").value
            var prey = individual.querySelector("input[name='prey']").checked
            var adult = individual.querySelector("input[name='adult']").checked
            var tagged = individual.querySelector("input[name='tagged']").checked
            var transmitter = individual.querySelector("input[name='transmitter']").checked
            var xmax = individual.querySelector("input[name='xmax']").value
            var xmin = individual.querySelector("input[name='xmin']").value
            var ymax = individual.querySelector("input[name='ymax']").value
            var ymin = individual.querySelector("input[name='ymin']").value

            row = {
                "chinese_common_name_by_ai": chinese_common_name_by_ai,
                "chinese_common_name_by_human": chinese_common_name_by_human,
                "medium_datetime": occurrences[object_id]["medium_datetime"],
                "medium_date": occurrences[object_id]["medium_date"],
                "perch_mount_id": occurrences[object_id]["perch_mount_id"],
                "perch_mount_name": occurrences[object_id]["perch_mount_name"],
                "main_behavior": main_behavior,
                "secondary_behavior": secondary_behavior,
                "prey": prey,
                "adult": adult,
                "tagged": tagged,
                "transmitter": transmitter,
                "object_id": object_id,
                "xamx": xmax,
                "xmin": xmin,
                "ymax": ymax,
                "ymin": ymin,
                "featured": featured,
            }
            confirmedData.push(row)
        }
    }
    var confirmSendButton = document.getElementById("confirm-send-button")
    data = { "data": confirmedData, "empty_ids": emptyObjectIds }
    confirmSendButton.value = JSON.stringify(data)
}