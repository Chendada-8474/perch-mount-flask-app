// var rawMedia = JSON.parse(document.getElementById("occurrence_info").textContent);
// var mediumTemplate = document.getElementById("medium_template").cloneNode(true)
// document.getElementById("medium_template").remove()
window.addEventListener("beforeunload", event => {
    event.preventDefault()
    event.returnValue = '';
})
const PERCISION = 1000
const MEDIA_CONTAINER_ID = "media-container"
const CONTENTSID = "contents"
const IMAGE_SIZE = [800, 600]

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
    class Media {
        constructor(mediumClassName) {
            this.mediumClassName = mediumClassName;
            this.childrenObjects = [];
            this.mediumTable = {};
            this.#getElements(this.mediumClassName)
        }

        shiftSelectChildren(start, end) {
            for (let i = start; i < end; i++) {
                this.childrenObjects[i].updateSelectionStatus(true);
            }
        }

        unSelectAll() {
            for (let child of this.childrenObjects) {
                child.updateSelectionStatus(false)
            }
        }

        #getElements(mediumClassName) {
            let media = document.getElementsByClassName(mediumClassName);
            for (let node of media) {
                var medium = new Medium(node, mediumClassName)
                this.childrenObjects.push(medium);
                this.mediumTable[medium.id] = medium;
            }
        }
    }

    class FullScreenImage {
        constructor(fullScreenImageId) {
            this.element = document.getElementById(fullScreenImageId);
        }

        show(url) {
            this.element.style.display = "block";
            this.element.style.backgroundImage = `url(${url})`;
        }
    }

    class Medium {
        constructor(element, mediumClassName) {
            this.id = element.id;
            this.element = element;
            this.mediumClassName = mediumClassName;
            this.individuals = this.#queryIndividuals();
            this.datetime = element.querySelector("input[name='medium_datetime']").value;
            this.path = element.querySelector("input[name='path']").value;
            this.fileName = element.querySelector("input[name='file_name']").value;
            this.eventSelect = element.querySelector("select[name='event']");
            this.isImage = element.querySelector("input[name='is_image']").checked;
            this.selectedInput = element.querySelector("input[name='temp-select']");
            this.modalIndividualTbody = element.querySelector("tbody");
            this.featureOpenButton = element.querySelector("button[name='feature_open']");
            this.featureTitleInput = element.querySelector("input[name='feature_title']");
            this.featureDescriptionInput = element.querySelector("input[name='feature_description']");
            this.featureBehaviorInput = element.querySelector("input[name='feature_behavior']");
            this.#activeSelectInput();
            this.#activeFullScreenImage();
            this.#activeEditModalTrigger();
            this.#activeFeatureOpen();
        }

        get_src() {
            let src = null
            if (this.isImage) {
                src = this.element.querySelector("img").src;
            } else {
                src = this.element.querySelector("video").src;
            }
            return src
        }

        updateInfo(info) {
            this.eventSelect.value = info['event'];

            for (let individual of Object.values(this.individuals)) {
                individual.updateInfo(info);
            }
        }

        updateSelectionStatus(toBool) {
            this.selectedInput.checked = toBool;
            this.#updateSelectionStyle(toBool);
        }

        deleteIndividual(individualId) {
            this.individuals[individualId].element.remove();
            delete this.individuals[individualId];
        }

        createIndividual(individualId, xmin, xmax, ymin, ymax) {
            let individualElement = this.#individualTemplate(individualId, xmin, xmax, ymin, ymax);
            this.modalIndividualTbody.appendChild(individualElement);
            this.individuals[individualId] = new Individual(individualId);
            feather.replace();
        }

        updateFeatureContent(title, description, behavior) {
            if (title !== null) {
                this.featureTitleInput.value = title;
            }
            if (description !== null) {
                this.featureDescriptionInput.value = description;
            }
            if (behavior !== null) {
                this.featureBehaviorInput.value = behavior;
            }
        }

        feature(doFeature) {
            if (doFeature) {
                this.featureOpenButton.setAttribute("class", "btn btn-danger btn-sm");
                this.featureOpenButton.children[0].classList.remove("text-secondary")
                this.featureOpenButton.children[0].classList.add("text-white")
            } else {
                this.featureOpenButton.setAttribute("class", "btn btn-white btn-sm")
                this.featureOpenButton.children[0].classList.remove("text-white")
                this.featureOpenButton.children[0].classList.add("text-secondary")
            }
        }

        getFeatureContent() {
            return {
                "title": this.featureTitleInput.value,
                "description": this.featureDescriptionInput.value,
            }
        }

        isFeatured() {
            if (this.featureBehaviorInput.value) {
                return true;
            } else {
                return false
            }
        }

        resize(width) {
            this.element.style.width = `${width}rem`
        }

        #queryIndividuals() {
            var individualElements = this.element.querySelectorAll("tbody > tr");
            var newIndividuals = {};
            for (let individual of individualElements) {
                newIndividuals[individual.id] = new Individual(individual.id);
            }
            return newIndividuals;
        }

        #activeEditModalTrigger() {
            var mediumObject = this
            this.element.querySelector("button[name='edit_modal_trigger']").addEventListener("click", function (event) {
                editModal.show(mediumObject)
            })
        }

        #updateSelectionStyle(checked) {
            if (checked) {
                this.element.classList.remove("border-0")
                this.element.classList.add("border-3")
            } else {
                this.element.classList.add("border-0")
                this.element.classList.remove("border-3")
            }
        }


        #activeSelectInput() {
            var thisMediumElement = this;
            var selectInput = this.element.querySelector("input[name='temp-select']");
            var className = this.mediumClassName
            selectInput.addEventListener("click", function (event) {
                thisMediumElement.#updateSelectionStyle(event.target.checked);
                if (event.target.checked) {
                    var child = event.target.closest(`.${className}`);
                    var parent = document.getElementById("contents");
                    var selectId = Array.prototype.indexOf.call(parent.children, child);

                    if (event.shiftKey) {
                        let start = Math.min(lastSelectMediumId, selectId) + 1;
                        let end = Math.max(lastSelectMediumId, selectId) + 1;
                        media.shiftSelectChildren(start, end);
                    } else {
                        lastSelectMediumId = selectId;
                    }
                }
            })
        }

        #activeFullScreenImage() {

            var image = this.element.querySelector("img");
            if (image) {
                image.addEventListener("click", function (event) {
                    fullScreenImage.show(event.target.src);
                })
            };
        };

        #activeFeatureOpen() {
            this.featureOpenButton.addEventListener("click", event => {
                let title = this.element.querySelector("input[name='feature_title']").value;
                let description = this.element.querySelector("input[name='feature_description']").value;
                let behavior = this.element.querySelector("input[name='feature_behavior']").value;
                featureEditer.updateMediumId(event.currentTarget.value);
                featureEditer.display(title, description, behavior);
            })
        }

        #individualTemplate(individualId, xmin, xmax, ymin, ymax) {
            let tr = document.createElement("tr")
            tr.setAttribute("id", individualId)
            tr.innerHTML = `
                <td class="ai-species align-middle">
                    <input type="text" name="ai_species" id="" value="" hidden>
                </td>
                <td class="align-middle">
                    <input list="species_list" type="text" name="common_ch_name"
                        class="form-control form-control-sm pm-review-species" size="10">
                </td>
                <td>
                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault" name="prey">
                </td>
                <td>
                    <button type="button" class="btn btn-white btn-sm" data-bs-toggle="dropdown" aria-expanded="false">
                        <i class="text-secondary" data-feather="more-vertical"></i>
                    </button>
                    <ul class="dropdown-menu p-2">
                        <li>
                            <input class="form-check-input" type="checkbox" id="flexCheckDefault" name="tagged">
                            <label class="form-check-label" for="flexCheckDefault">標記</label>
                        </li>
                        <li>
                            <label for="ring_number_input">環號</label>
                            <input id="ring_number_input" class="form-control form-control-sm" type="text" value="" name="ring_number">
                        </li>
                    </ul>
                    <button type="button" class="btn btn-outline-danger btn-sm border-0" value="${individualId}" name="main_medium_indivudal_id">
                        <i class="hover-pointer" data-feather="trash-2"></i>
                    </button>
                </td>
                <td hidden>
                    <input type="number" step="0.001" name="xmax" value=${xmax} hidden>
                    <input type="number" step="0.001" name="xmin" value=${xmin} hidden>
                    <input type="number" step="0.001" name="ymax" value=${ymax} hidden>
                    <input type="number" step="0.001" name="ymin" value=${ymin} hidden>
                </td>
            `
            return tr;
        }
    }

    class Individual {
        constructor(individualId) {
            this.id = individualId;
            this.element = document.getElementById(individualId);
            this.aiSpecies = this.element.querySelector("input[name='ai_species']").value;
            this.xmin = this.element.querySelector("input[name='xmin']").value;
            this.xmax = this.element.querySelector("input[name='xmax']").value;
            this.ymin = this.element.querySelector("input[name='ymin']").value;
            this.ymax = this.element.querySelector("input[name='ymax']").value;
            this.inputBox = this.element.querySelector("input[name='common_ch_name']");
            this.#activeSpeciesNamePredict();
            this.#activeDeleteButton();
        }


        updateInfo(info) {
            this.inputBox.value = info["speciesName"];
            this.element.querySelector("input[name='ring_number']").value = info["ringNumber"];
            this.element.querySelector("input[name='prey']").checked = info["prey"];
            this.element.querySelector("input[name='tagged']").checked = info["tagged"];
        }

        updateSpeciesName(speicesName) {
            this.inputBox.value = speicesName;
        }

        #activeDeleteButton() {
            this.element.querySelector("button[name='main_medium_indivudal_id']").addEventListener("click", deleteIndividual);
        }

        #activeSpeciesNamePredict() {
            this.inputBox.addEventListener("input", searchSpecies)
        }
    }

    class EditModal {
        constructor(editModalId) {
            this.mediumIdShowing = null;
            this.element = document.getElementById(editModalId);
            this.addIndivudalButton = document.getElementById("edit_add_individual");
            this.titleElement = document.getElementById("editModalLabel");
            this.imageElement = this.element.querySelector("img");
            this.videoElement = this.element.querySelector("video");
            this.individualTemplate = this.#individualTemplate();
            this.modalIndividualTbody = this.element.querySelector("tbody");
            this.#initImageSize();
            this.#activeViideoAddIndividual();
            // this.imageRangeElement = this.element.querySelector("input[name='image_size']");
            // this.#activeImageRange();
        }

        show(medium) {
            this.mediumIdShowing = medium.id;
            this.titleElement.innerHTML = medium.fileName;
            boundingBoxCotroller.clearBoxes();
            this.#display(medium);
            this.#displayInformation(medium);
            this.#displayIndividuals(medium);
        }

        #display(medium) {
            var src = medium.get_src()
            if (medium.isImage) {
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
            document.getElementById("info_object_id").innerHTML = medium.id;
            document.getElementById("info_medium_datetime").innerHTML = medium.datetime;
            document.getElementById("info_file_name").innerHTML = medium.fileName;
            document.getElementById("info_path").innerHTML = medium.path;

        }

        #displayIndividuals(medium) {
            this.modalIndividualTbody.innerHTML = "";

            var individuals = medium.individuals;

            for (let individual of Object.values(individuals)) {
                let aiSpecies = individual.aiSpecies;
                let humanSpecies = individual.inputBox.value;
                let xmin = individual.xmin;
                let xmax = individual.xmax;
                let ymin = individual.ymin;
                let ymax = individual.ymax;

                this.createIndividualElement(aiSpecies, humanSpecies, xmin, xmax, ymin, ymax, individual.id);

                // let inputElement = element.querySelector("input[name='common_ch_name']");

                if (humanSpecies) {
                    var speciesName = humanSpecies;
                } else {
                    var speciesName = aiSpecies;
                }

                let boundingBox = new BoundingBox(individual.id, speciesName, xmin, xmax, ymin, ymax, IMAGE_SIZE);
                boundingBoxCotroller.addBox(boundingBox);
                // boundingBoxCotroller.element.appendChild(boundingBox.element);

                colorManager.next();
            }
        }

        createIndividualElement(aiName, humanSpecies, xmin, xmax, ymin, ymax, individualId) {
            // var element = document.createElement("tr");
            // element.setAttribute("id", individualId + "_edit")
            let element = this.#individualTemplate(individualId, aiName, xmin, xmax, ymin, ymax);

            let deleteButton = element.querySelector("button[name='edit_individual_id']");
            deleteButton.addEventListener('click', event => deleteIndividual(event))

            let inputElement = element.querySelector("input[name='common_ch_name']");
            inputElement.addEventListener("input", searchSpecies);
            inputElement.addEventListener("focusout", event => updateMediumSpeciesName(event));

            inputElement.value = humanSpecies;

            element.querySelector("input[name='point_individual_id']").value = individualId;
            this.modalIndividualTbody.appendChild(element);
            feather.replace();
            // return element;
        }

        deleteIndividualElement(individualId) {
            document.getElementById(`${individualId}_edit`).remove();
        }

        #activeImageRange() {
            let modal = this;
            this.imageRangeElement.addEventListener("input", function (event) {
                modal.#setImageRange(event.target.value);
            })
        }

        #activeViideoAddIndividual() {
            this.addIndivudalButton.addEventListener("click", event => {
                addIndividual();
            })
        }

        #setImageRange(width) {
            this.imageElement.style.width = `${width}rem`;
            this.videoElement.style.width = `${width}rem`;
        }

        #initImageSize() {
            this.imageElement.style.width = IMAGE_SIZE[0];
            this.imageElement.style.height = IMAGE_SIZE[1];
        }

        #individualTemplate(individualId, aiSpeciesName, xmin, xmax, ymin, ymax) {
            let colorClass = colorManager.assigneColor()["mainColor"];
            let tr = document.createElement("tr");
            tr.setAttribute("id", individualId + "_edit");
            tr.innerHTML = `
                <td class="align-middle">
                    <div class="border border-secondary rounded-circle rounded-circle bg-${colorClass} bg-opacity-75" style="width: 15px; height: 15px;"></div>
                </td>
                <td class="ai-species" scope="row">${aiSpeciesName}</td>
                <td scope="row">
                    <input class="form-control form-control-sm human-species" type="text" name="common_ch_name" size=8>
                </td>
                <td class="xmax" scope="row">${xmax}</td>
                <td class="xmin" scope="row">${xmin}</td>
                <td class="ymax" scope="row">${ymax}</td>
                <td class="ymin" scope="row">${ymin}</td>
                <td>
                    <button type="button" class="btn btn-outline-danger btn-sm border-0" name="edit_individual_id" value=${individualId}>
                        <i data-feather="trash-2"></i>
                    </button>
                </td>
                <td hidden>
                    <input name="point_individual_id" type="text" hidden>
                </td>
            `
            return tr;
        }

        removeIndividual(individualId) {
            document.getElementById(individualId + "_edit").remove();
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

    class Updater {
        constructor() {
            this.speciesName = document.getElementById("edit-species");
            this.confirmButton = document.getElementById("confirm-edit");
            this.#listenConfirm();
            this.#listenSpeciesInput();
            this.#listenStartButton();
        }


        #updateMediumInfo() {

            var speciesName = document.getElementById("edit-species").value;
            var ringNumber = document.getElementById("edit-ring-number").value;
            var _event = document.getElementById("edit-event").value;
            var prey = document.getElementById("edit-prey").checked;
            var tagged = document.getElementById("edit-tagged").checked;
            var values = {
                "speciesName": speciesName,
                "ringNumber": ringNumber,
                "event": _event,
                "prey": prey,
                "tagged": tagged,
            }

            for (let medium of media.childrenObjects) {
                if (medium.selectedInput.checked) {
                    medium.updateInfo(values);
                }
            }

        }

        #listenConfirm() {
            this.confirmButton.addEventListener("click", this.#updateMediumInfo)
        }

        #listenSpeciesInput() {
            this.speciesName.addEventListener("input", searchSpecies);
        }

        #listenStartButton() {
            document.getElementById("start_edit").addEventListener("click", this.#resetValues)
        }

        #resetValues() {
            document.getElementById("edit-species").value = "";
            document.getElementById("edit-ring-number").value = "";
            document.getElementById("edit-event").value = "";
            document.getElementById("edit-prey").value = "";
            document.getElementById("edit-tagged").value = "";
        }
    }

    class FeatureEditer {
        constructor() {
            this.element = document.getElementById("featuring_medium_id");
            this.titleElement = document.getElementById("featured_title");
            this.behaviorElement = document.getElementById("featured_behavior");
            this.descriptionElement = document.getElementById("featured_description");
            this.mediumIdDirecting = document.getElementById("featuring_medium_id");
            this.saveChangeButton = document.getElementById("feature_save");
            this.#activeContentInput();
            this.#activeSaveChange();
        }

        display(title, description, behavior) {
            this.titleElement.value = title;
            this.behaviorElement.value = behavior;
            this.descriptionElement.value = description;

        }

        updateMediumId(mediumId) {
            this.mediumIdDirecting.value = mediumId;
        }

        #activeContentInput() {
            this.titleElement.addEventListener("input", event => {
                media.mediumTable[this.mediumIdDirecting.value].updateFeatureContent(event.target.value, null, null);
            })
            this.descriptionElement.addEventListener("input", event => {
                media.mediumTable[this.mediumIdDirecting.value].updateFeatureContent(null, event.target.value, null)
            })
            this.behaviorElement.addEventListener("input", event => {
                media.mediumTable[this.mediumIdDirecting.value].updateFeatureContent(null, null, event.target.value)
            })
        }

        #activeSaveChange() {
            this.saveChangeButton.addEventListener("click", event => {
                if (this.behaviorElement.value) {
                    media.mediumTable[this.mediumIdDirecting.value].feature(true);
                } else {
                    media.mediumTable[this.mediumIdDirecting.value].feature(false);
                }
            });
        }
    }

    class PreferenceSetter {
        constructor() {
            this.imageSize = document.getElementById("imageSizeRange");
            this.#activeImageSizeRange()
        }
        #activeImageSizeRange() {
            this.imageSize.addEventListener("input", event => {
                document.cookie = `review_img_size=${event.target.value}`
                for (let medium of media.childrenObjects) {
                    medium.resize(event.target.value);
                }
            })
        }
    }

    class DataDispatcher {
        constructor() {
            this.confirmButton = document.getElementById("open-confirm-modal");
            this.submitButton = document.getElementById("confirm-send-button");
            this.speciesList = document.getElementById("confirm-species-list");
            this.#activeConfirm();
        }

        clearSpecies() {
            this.speciesList.innerHTML = "";

        }

        addSpecies(speciesName) {
            let li = document.createElement("li");
            li.classList.add("list-group-item");
            li.innerHTML = speciesName;
            this.speciesList.appendChild(li);
        }

        disableSubmit() {
            this.submitButton.style.display = "none";
        }

        enableSubmit() {
            this.submitButton.style.display = "block";
        }

        #activeConfirm() {
            this.confirmButton.addEventListener("click", lookupCommonName)
        }


        getIdNamePair() {
            var commonNames = [];
            var individualIds = [];
            for (let medium of media.childrenObjects) {
                for (let individual of Object.values(medium.individuals)) {
                    individualIds.push(individual.id);
                    if (individual.inputBox.value) {
                        commonNames.push(individual.inputBox.value);
                    } else {
                        commonNames.push(individual.aiSpecies);
                    }

                }
            }

            return { "commonName": commonNames, "individualId": individualIds }
        }


    }
    var xhr = new XMLHttpRequest()
    var colorManager = new ColorAssigner();
    var media = new Media("pm-media");
    var fullScreenImage = new FullScreenImage("full_screen_image");
    var editModal = new EditModal("editModal");
    var boundingBoxCotroller = new BoundingBoxController();
    var drawingBoundingBox = new DrawingBoundingBox(0, 0);
    var update = new Updater("updater");
    var featureEditer = new FeatureEditer();
    var preference = new PreferenceSetter();
    var datadispatcher = new DataDispatcher();

    var lastSelectMediumId = 0;


    if (getCookieByName("review_img_size")) {
        media.childrenObjects.forEach(element => {
            element.resize(getCookieByName("review_img_size"));
        })
    }


    // unselect all select input when clicked background
    var mediaContainer = document.getElementById(MEDIA_CONTAINER_ID);
    mediaContainer.addEventListener("click", function (event) {
        let targetId = event.target.id;
        if (targetId == MEDIA_CONTAINER_ID || targetId == CONTENTSID) {
            media.unSelectAll();
        }
    })



    function lookupCommonName() {

        document.getElementById("name_alert").style.display = "none"

        for (let medium of media.childrenObjects) {
            for (let individual of Object.values(medium.individuals)) {
                individual.element.classList.remove("bg-danger");
            }
        }

        var IdNamePair = datadispatcher.getIdNamePair();
        console.log(IdNamePair)
        xhr.open("post", "/lookup_common_name", true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(IdNamePair.commonName));
        xhr.onload = function () {
            var inputError = false;
            if (xhr.status != 200) {
                return;
            }
            var results = JSON.parse(xhr.responseText);
            for (let i = 0; i < results.length; i++) {
                if (!results[i]) {
                    document.getElementById(IdNamePair.individualId[i]).classList.add("bg-opacity-50");
                    document.getElementById(IdNamePair.individualId[i]).classList.add("bg-danger");
                    inputError = true;
                }
            }
            if (inputError) {
                datadispatcher.disableSubmit();
                document.getElementById("name_alert").style.display = "block"
            } else {
                let species = new Set(IdNamePair.commonName);
                datadispatcher.clearSpecies();
                for (let sp of species) {
                    datadispatcher.addSpecies(sp);
                }
                datadispatcher.enableSubmit();
            }
        }
    }

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

    function updateMediumSpeciesName(event) {
        let speciesName = event.target.value;
        let mediumId = event.target.closest("tr").id.split("_")[0];
        let individualId = event.target.closest("tr").id.slice(0, -5);
        media.mediumTable[mediumId].individuals[individualId].updateSpeciesName(speciesName);
    }

    function deleteIndividual(event) {
        var individualId = event.currentTarget.value;
        var mediumId = individualId.split("_")[0];
        boundingBoxCotroller.deleteBox(individualId);
        media.mediumTable[mediumId].deleteIndividual(individualId);
        if (event.currentTarget.name == "edit_individual_id") {
            editModal.deleteIndividualElement(individualId);
        }
    }

    function addIndividual() {
        var newSpeciesId = `${editModal.mediumIdShowing}_indi_${boundingBoxCotroller.giveMeNewBoxIndex()}`;
        if (media.mediumTable[editModal.mediumIdShowing].isImage) {
            var rect = drawingBoundingBox.getRectangleMinMax();
            var newBoundingBox = new BoundingBox(newSpeciesId, "untitle", rect.xmin, rect.xmax, rect.ymin, rect.ymax, IMAGE_SIZE);
            boundingBoxCotroller.addBox(newBoundingBox);
            editModal.createIndividualElement("", "", rect.xmin, rect.xmax, rect.ymin, rect.ymax, newSpeciesId);
            media.mediumTable[editModal.mediumIdShowing].createIndividual(newSpeciesId, rect.xmin, rect.xmax, rect.ymin, rect.ymax);
        } else {
            editModal.createIndividualElement("", "", "", "", "", "", newSpeciesId);
            media.mediumTable[editModal.mediumIdShowing].createIndividual(newSpeciesId, "", "", "", "");
        }
        colorManager.next();
    }

    function getCookieByName(name) {
        return document.cookie
            .split("; ")
            .find((row) => row.startsWith(`${name}=`))
            ?.split("=")[1];
    }

});