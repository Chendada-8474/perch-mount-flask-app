const IMAGE_SIZE = [800, 600]
const PERCISION = 1000

class ColorAssigner {
    #color = ["primary", "success", "danger", "warning", "info", "light", "dark", "secondary"]
    #textColor = ["white", "white", "white", "black", "black", "black", "white", "white"]
    #numberOfColor = this.#textColor.length;
    #order = 0;

    assigneColor() {
        let index = this.#order % this.#numberOfColor;
        let result = {
            "mainColor": this.#color[index],
            "textColor": this.#textColor[index],
        };
        return result;
    }

    next() {
        this.#order ++;
    }

    resetOrder() {
        this.#order = 0;
    }

}


document.addEventListener("DOMContentLoaded", () => {

    class EditModal {
        constructor(editModalId) {
            this.mediumIdShowing = null;
            this.element = document.getElementById(editModalId);
            this.addIndivudalButton = document.getElementById("edit_add_individual");
            this.titleElement = document.getElementById("editModalLabel");
            this.imageElement = this.element.querySelector("img");
            this.videoElement = this.element.querySelector("video");
            this.modalIndividualTbody = this.element.querySelector("tbody");
            this.editContent = document.getElementById("edit-content");
            this.noDataAlert = document.getElementById("no-data");
            this.#initImageSize();
            this.#activeViideoAddIndividual();
        }

        hide() {
            this.editContent.style.display = "none";
        }

        show(medium) {
            this.file_type = medium[0].file_type;
            this.mediumIdShowing = medium[0].object_id;
            boundingBoxCotroller.clearBoxes();
            this.#display(medium);
            this.#displayInformation(medium);
            this.#displayIndividuals(medium);
            this.editContent.style.display = "block";
        }

        hideAlert() {
            this.noDataAlert.style.display = "none";
        }

        showAlert() {
            this.noDataAlert.style.display = "block";
        }

        #display(medium) {
            var src = "/uploads/" + medium[0].path
            if (medium[0].file_type == "image") {
                boundingBoxCotroller.element.style.display = "block";
                this.imageElement.src = src;
                this.imageElement.style.display = "block";
                this.videoElement.style.display = "none";
                this.addIndivudalButton.style.display = "none";
            } else {
                this.videoElement.src = src;
                this.videoElement.style.display = "block";
                this.imageElement.style.display = "none";
                this.addIndivudalButton.style.display = "block";
                boundingBoxCotroller.element.style.display = "none";
            }
        }

        #displayInformation(medium) {
            document.getElementById("info_object_id").innerHTML = medium[0].object_id;
            document.getElementById("info_medium_datetime").innerHTML = medium[0].medium_datetime;
            document.getElementById("info_path").innerHTML = medium[0].path;
            document.getElementById("info_perch_mount_name").innerHTML = medium[0].perch_mount_name;
            document.getElementById("info_file_type").innerHTML = medium[0].file_type;
        }

        #displayIndividuals(medium) {
            let individualIndex = 0;

            this.modalIndividualTbody.innerHTML = "";

            for (let individual of medium) {
                let individualId = `${individual.object_id}_${individualIndex}`
                if (individual.ring_number == "null") {
                    var ringNumber = individual.ring_number;
                } else {
                    var ringNumber = "";
                }
                let individualInfo = {
                    "individualId": individualId,
                    "aiSpecies": individual.common_name_by_ai,
                    "humanSpecies": individual.common_name_by_human,
                    "xmin": individual.xmin,
                    "xmax": individual.xmax,
                    "ymin": individual.ymin,
                    "ymax": individual.ymax,
                    "prey": individual.prey,
                    "tagged": individual.tagged,
                    "ringNumber": ringNumber,
                }

                this.createIndividualElement(individualInfo);
                individualIndex++;
                let boundingBox = new BoundingBox(
                    individualId,
                    individual.common_name_by_human,
                    individual.xmin,
                    individual.xmax,
                    individual.ymin,
                    individual.ymax,
                    IMAGE_SIZE
                );
                boundingBoxCotroller.addBox(boundingBox);
                colorManager.next();
            }
        }

        createIndividualElement(individualInfo) {
            let humanSpecies = individualInfo.humanSpecies
            let individualId = individualInfo.individualId
            let element = this.#individualTemplate(individualInfo);

            let deleteButton = element.querySelector("button[name='edit_individual_id']");
            deleteButton.addEventListener('click', event => deleteIndividual(event))

            let inputElement = element.querySelector("input[name='common_ch_name']");
            inputElement.addEventListener("input", searchSpecies);

            inputElement.value = humanSpecies;

            element.querySelector("input[name='point_individual_id']").value = individualId;
            this.modalIndividualTbody.appendChild(element);
            feather.replace();
            // return element;
        }

        deleteIndividualElement(individualId) {
            document.getElementById(individualId).remove();
        }

        #activeViideoAddIndividual() {
            this.addIndivudalButton.addEventListener("click", event => {
                addIndividual();
            })
        }

        #initImageSize() {
            this.imageElement.style.width = IMAGE_SIZE[0];
            this.imageElement.style.height = IMAGE_SIZE[1];
        }

        #individualTemplate(individualInfo) {
            let colorClass = colorManager.assigneColor()["mainColor"];
            let tr = document.createElement("tr");
            let preyChecked = "";
            let taggedChecked = "";
            if (individualInfo.prey) {
                preyChecked = "checked"
            }
            if (individualInfo.tagged) {
                taggedChecked = "checked"
            }
            tr.setAttribute("id", individualInfo.individualId);
            tr.innerHTML = `
                <td class="align-middle">
                    <div class="border border-secondary rounded-circle rounded-circle bg-${colorClass} bg-opacity-75" style="width: 15px; height: 15px;"></div>
                </td>
                <td class="ai-species" scope="row">${individualInfo.aiSpecies}</td>
                <td scope="row">
                    <input class="form-control form-control-sm human-species" type="text" name="common_ch_name" size=8>
                </td>
                <td class="xmax" scope="row">${individualInfo.xmax}</td>
                <td class="xmin" scope="row">${individualInfo.xmin}</td>
                <td class="ymax" scope="row">${individualInfo.ymax}</td>
                <td class="ymin" scope="row">${individualInfo.ymin}</td>
                <input type="number" step="0.01" name="xmax" value=${individualInfo.xmax} hidden>
                <input type="number" step="0.01" name="xmin" value=${individualInfo.xmin} hidden>
                <input type="number" step="0.01" name="ymax" value=${individualInfo.ymax} hidden>
                <input type="number" step="0.01" name="ymin" value=${individualInfo.ymin} hidden>
                <td>
                    <button type="button" class="btn btn-outline-danger btn-sm border-0" name="edit_individual_id" value=${individualInfo.individualId}>
                        <i data-feather="trash-2"></i>
                    </button>
                </td>
                <td class="ymin" scope="row">
                    <button type="button" class="btn btn-while btn-sm" data-bs-toggle="dropdown" aria-expanded="false">
                        <i data-feather="more-vertical"></i>
                    </button>
                    <ul class="dropdown-menu p-3">
                        <li>
                            <input name="prey" class="form-check-input" type="checkbox" id="flexCheckDefault" ${preyChecked}>
                            <label class="form-check-label" for="flexCheckDefault">獵物</label>
                        </li>
                        <li>
                            <input name="tagged" class="form-check-input" type="checkbox" value="" id="flexCheckDefault" ${taggedChecked}>
                            <label class="form-check-label" for="flexCheckDefault">標記</label>
                        </li>
                        <li>
                            <label class="form-check-label" for="flexCheckDefault">環號</label>
                            <input name="ring_number" class="form-control form-control-sm" type="text" value="${individualInfo.ringNumber}" id="flexCheckDefault">
                        </li>
                    </ul> 
                </td>
                <td hidden>
                    <input name="point_individual_id" type="text" hidden>
                </td>
            `
            return tr;
        }

        removeIndividual(individualId) {
            document.getElementById(individualId).remove();
        }
    }



    class BoundingBoxController {
        #newBoxindex = 10000;
        constructor() {
            this.element = document.getElementById("boxing-container");
            this.canvas = document.getElementById("bounding-box-painter");
            this.image = this.element.querySelector("img");
            this.horizontalLine = document.getElementById("horizontal");
            this.verticalLine = document.getElementById("vertical");
            this.x = document.getElementById("painter_x");
            this.y = document.getElementById("painter_y");
            this.boxes = {};
            this.mouseDown = false;
            this.#currentMousePosisionOnImage();
            this.#imageListenerForSettingPainter();
            this.#activeMousedownListener();
            this.#activeMouseupListener();
        }

        clearBoxes() {
            for (let box of Object.values(this.boxes)) {
                box.element.remove();
            }
            this.boxes = {};
        }

        deleteBox(individualId) {
            if (this.boxes[individualId]) {
                this.boxes[individualId].element.remove();
                delete this.boxes[individualId];
            }
        }

        addBox(box) {
            this.element.appendChild(box.element)
            this.boxes[box.individualDirectId] = box;
        }


        getImageSize() {
            return [this.image.offsetWidth, this.image.offsetHeight]
        }

        setPainterSize() {
            let size = this.getImageSize();
            this.canvas.style.height = `${size[1]}px`;
            this.canvas.style.width = `${size[0]}px`;
        }

        resetRefLine() {
            this.horizontalLine.style.height = "0px"
            this.verticalLine.style.width = "0px"
        }


        #currentMousePosisionOnImage() {
            let h = this.horizontalLine;
            let v = this.verticalLine;
            let x = this.x;
            let y = this.y;
            this.canvas.addEventListener("mousemove", event => {
                let originX = event.target.getBoundingClientRect().left;
                let originY = event.target.getBoundingClientRect().top;
                h.style.width = `${event.target.offsetWidth}px`;
                h.style.height = `${event.clientY - originY}px`;
                v.style.width = `${event.clientX - originX}px`;
                v.style.height = `${event.target.offsetHeight}px`;
                x.innerHTML = Math.round((event.clientX - originX) / event.target.offsetWidth * PERCISION) / PERCISION;
                y.innerHTML = Math.round((event.clientY - originY) / event.target.offsetHeight * PERCISION) / PERCISION;

                if (this.mouseDown) {
                    drawingBoundingBox.sizing(event.clientX - originX, event.clientY - originY);
                }
            })
        }

        #imageListenerForSettingPainter() {
            this.image.addEventListener("mouseover", event => {
                this.setPainterSize();
            })
        }

        #activeMousedownListener() {
            this.element.addEventListener("mousedown", event => {
                this.mouseDown = true;
                let originX = event.target.getBoundingClientRect().left;
                let originY = event.target.getBoundingClientRect().top;
                drawingBoundingBox.resetInit(event.clientX - originX, event.clientY - originY)
                drawingBoundingBox.display()
            })
        }

        #activeMouseupListener() {
            this.element.addEventListener("mouseup", event => {
                this.mouseDown = false;
                drawingBoundingBox.hide();
                addIndividual();
            })
        }
        giveMeNewBoxIndex() {
            ++this.#newBoxindex;
            return this.#newBoxindex;
        }
    }

    class DrawingBoundingBox {
        constructor(initX, initY) {
            this.initX = initX;
            this.initY = initY;
            this.left = initX;
            this.top = initY;
            this.element = this.#createThis();
        }

        #createThis() {
            let element = document.createElement("div");
            let classes = ["position-absolute", "rounded", "border", "border-secondary-subtle", "border-3", "border-opacity-25"]

            element.setAttribute("id", "new_boundind_box");
            classes.forEach(c => { element.classList.add(c) })
            element.style.display = "none";
            boundingBoxCotroller.element.appendChild(element);
            return element;
        }

        resetInit(initX, initY) {
            this.initX = initX;
            this.initY = initY;
        }

        display() {
            this.element.style.display = "block";
        }

        hide() {
            this.element.style.display = "none";
        }

        sizing(newX, newY) {
            this.left = Math.min(newX, this.initX);
            this.top = Math.min(newY, this.initY);
            this.width = Math.max(newX, this.initX) - this.left;
            this.height = Math.max(newY, this.initY) - this.top;
            this.element.style.left = `${this.left}px`;
            this.element.style.top = `${this.top}px`;
            this.element.style.width = `${this.width}px`;
            this.element.style.height = `${this.height}px`;
        }

        getRectangleMinMax() {
            let values = {
                "xmin": Math.round((this.left / IMAGE_SIZE[0] * PERCISION)) / PERCISION,
                "xmax": Math.round((this.left + this.width) / IMAGE_SIZE[0] * PERCISION) / PERCISION,
                "ymin": Math.round(this.top / IMAGE_SIZE[1] * PERCISION) / PERCISION,
                "ymax": Math.round((this.top + this.height) / IMAGE_SIZE[1] * PERCISION) / PERCISION,
            };
            return values;
        }
    }

    class BoundingBox {
        constructor(individualId, commonName, xmin, xmax, ymin, ymax, imageSize) {
            this.xmin = xmin;
            this.xmax = xmax;
            this.ymin = ymin;
            this.ymax = ymax;
            this.individualDirectId = individualId;
            this.commonName = commonName;

            this.left = Math.round(imageSize[0] * xmin);
            this.top = Math.round(imageSize[1] * ymin);
            this.width = Math.round(imageSize[0] * xmax - this.left);
            this.height = Math.round(imageSize[1] * ymax - this.top);

            this.template = this.#boxDivTempldate();
            this.element = this.#createThisElement();
        }

        #createThisElement() {
            var color = colorManager.assigneColor();

            var box = document.createElement("div");
            box.innerHTML = this.template;
            box = box.children[0];

            box.classList.add(`border-${color.mainColor}`)

            box.style.top = `${this.top}px`;
            box.style.left = `${this.left}px`;
            box.style.width = `${this.width}px`;
            box.style.height = `${this.height}px`;

            var speciesTag = box.querySelector("span");
            speciesTag.innerHTML = this.commonName;
            speciesTag.classList.add(`bg-${color.mainColor}`)
            speciesTag.classList.add(`text-${color.textColor}`)
            speciesTag.classList.add("opacity-75")

            box.querySelector("input").innerHTML = this.individualDirectId;
            return box;
        }

        #boxDivTempldate() {
            let template = `
            <div class="border border-5 border-opacity-75 position-absolute rounded">
                <span class="position-absolute bottom-0 start-0 p-1 rounded"></span>
                <input type="text" name="individual_id" hidden>
            </div>
            `
            return template;
        }


    }

    var colorManager = new ColorAssigner();
    var editModal = new EditModal("editModal");
    var boundingBoxCotroller = new BoundingBoxController();
    var drawingBoundingBox = new DrawingBoundingBox(0, 0);
    var xhr = new XMLHttpRequest()
    var searchButton = document.getElementById("search_occurrence");
    var individualContainer = document.getElementById("edit_modal_individuals");
    var successAlert = document.getElementById("insert_success");
    var failAlert = document.getElementById("insert_fail");

    function deleteIndividual(event) {
        var individualId = event.currentTarget.value;
        boundingBoxCotroller.deleteBox(individualId);
        if (event.currentTarget.name == "edit_individual_id") {
            editModal.deleteIndividualElement(individualId);
        }
    }


    function addIndividual() {
        var newSpeciesId = `${editModal.mediumIdShowing}_${boundingBoxCotroller.giveMeNewBoxIndex()}`;

        if (editModal.file_type == "image") {
            var rect = drawingBoundingBox.getRectangleMinMax();
            var newBoundingBox = new BoundingBox(newSpeciesId, "untitle", rect.xmin, rect.xmax, rect.ymin, rect.ymax, IMAGE_SIZE);
            let individualInfo = {
                "individualId": newSpeciesId,
                "aiSpecies": "",
                "humanSpecies": "",
                "xmin": rect.xmin,
                "xmax": rect.xmax,
                "ymin": rect.ymin,
                "ymax": rect.ymax,
                "prey": "",
                "tagged": "",
                "ringNumber": "",
            }
            boundingBoxCotroller.addBox(newBoundingBox);
            editModal.createIndividualElement(individualInfo);
        } else {
            let individualInfo = {
                "individualId": newSpeciesId,
                "aiSpecies": "",
                "humanSpecies": "",
                "xmin": "",
                "xmax": "",
                "ymin": "",
                "ymax": "",
                "prey": "",
                "tagged": "",
                "ringNumber": "",
            }
            editModal.createIndividualElement(individualInfo);
        }
        colorManager.next();
    }


    searchButton.addEventListener("click", event => {
        let objectId = document.getElementById("object_id").value;
        let meidiumDate = document.getElementById("medium_date").value;
        editModal.hide();
        editModal.hideAlert();
        if (objectId && meidiumDate) {
            xhr.open("get", `/update_medium/${meidiumDate}/${objectId}`, true);
            xhr.send();
            xhr.onload = function () {
                if (xhr.status != 200) {
                    return;
                }
                var medium = JSON.parse(xhr.responseText);
                if (medium.length) {
                    editModal.show(medium)
                } else {
                    editModal.showAlert();
                }
            }
        } else {
            editModal.showAlert();
        }

    })

    function searchSpecies(event) {
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

    document.getElementById("send_data").addEventListener("click", evnet => {
        !checkCommonName()
    })

    function checkCommonName() {
        var names = [];
        var inputs = document.getElementsByName("common_ch_name");
        for (let input of inputs) {
            names.push(input.value);
        }
        xhr.open("post", "/lookup_common_name", true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(names));
        xhr.onload = function () {
            var pass = true;
            if (xhr.status == 200) {
                var results = JSON.parse(xhr.responseText)
                for (let i = 0; i < results.length; i++) {
                    if (!results[i]) {
                        pass = false;
                        inputs[i].classList.add("bg-opacity-50");
                        inputs[i].classList.add("bg-danger");
                    } else {
                        inputs[i].classList.remove("bg-opacity-50");
                        inputs[i].classList.remove("bg-danger");
                    }
                }
                if (pass) {
                    var rows = getMediumInfo();
                    insertToBigquery(rows);
                }
            }
        };


    }

    function getMediumInfo() {
        rows = [];
        var objectId = document.getElementById("info_object_id").innerHTML;
        var mediumDatetime = document.getElementById("info_medium_datetime").innerHTML;
        var perchMountName = document.getElementById("info_perch_mount_name").innerHTML;
        var fileType = document.getElementById("info_file_type").innerHTML;
        for (let individual of individualContainer.children) {
            rows.push({
                "object_id": objectId,
                "medium_datetime": mediumDatetime,
                "perch_mount_name": perchMountName,
                "file_type": fileType,
                "common_name_by_ai": individual.getElementsByClassName("ai-species")[0].innerHTML,
                "common_name_by_human": individual.querySelector("input[name='common_ch_name']").value,
                "prey": individual.querySelector("input[name='prey']").checked,
                "tagged": individual.querySelector("input[name='tagged']").checked,
                "ring_number": individual.querySelector("input[name='ring_number']").value,
                "xmax": individual.querySelector("input[name='xmax']").value,
                "xmin": individual.querySelector("input[name='xmin']").value,
                "ymax": individual.querySelector("input[name='ymax']").value,
                "ymin": individual.querySelector("input[name='ymin']").value,
            })
        }
        return { "rows": JSON.stringify(rows) };
    }

    function insertToBigquery(rows) {
        let objectId = document.getElementById("object_id").value;
        let meidiumDate = document.getElementById("medium_date").value;
        xhr.open("post", `/update_medium/${meidiumDate}/${objectId}`, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(rows));
        xhr.onload = function () {
            if (xhr.status != 200) {
                return;
            }
            var mes = JSON.parse(xhr.responseText)["message"]
            if (!mes) {
                failAlert.style.display = "block"
                successAlert.style.display = "none"
            } else {
                failAlert.style.display = "none"
                successAlert.style.display = "block"
            }
        }

    };
}
)