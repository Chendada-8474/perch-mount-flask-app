


class Media {
    clear() {

    }
}


class Medium {
    createIndex = 0;
    constructor(featureInfo) {
        this.info = featureInfo;
    }

    createElement(mediumInfo) {
        let html = this.#htmlTemplate();
        let container = document.createElement("div");
        // let mediumId = `${mediumInfo["object_id"]}_${this.createIndex}`
        let mediumId = mediumInfo.feature_medium_id
        this.createIndex++;
        container.innerHTML = html;
        container.querySelector("div.pm-media").id = mediumId;
        container.querySelector("h5").innerHTML = mediumInfo["title"];

        container.querySelector("button.download-medium").value = mediumInfo["object_id"];

        container.querySelector("button.collapse-button").setAttribute("data-bs-target", `#collapse_${mediumId}`);
        container.querySelector("button.collapse-button").setAttribute("aria-controls", `collapse_${mediumId}`);

        // append species badge and behavior badge
        let badgeContainer = container.querySelector("div.badge-container");
        badgeContainer.appendChild(this.#createBadge(mediumInfo["species"]));
        badgeContainer.appendChild(this.#createBadge(mediumInfo["behavior"]));

        // write collapse infomation
        let collapse = container.querySelector("div.collapse");
        let collapseBody = collapse.querySelector("div.card");
        collapse.id = `collapse_${mediumId}`;
        for (let [field, content] of Object.entries(mediumInfo)) {
            let newInfo = document.createElement("p");
            newInfo.classList.add("m-0");
            newInfo.innerHTML = `${field}: ${content}`;
            collapseBody.appendChild(newInfo);
        }

        // image or video
        let image = container.querySelector("img");
        let video = container.querySelector("video");
        if (mediumInfo["is_image"]) {
            image.src = `/uploads/${mediumInfo["path"]}`;
            video.remove();
        } else {
            video.src = `/uploads/${mediumInfo["path"]}`;
            image.remove();
        }

        container.querySelector("button.download-medium").addEventListener("click", downloadMedium);
        container.querySelector("button.delete-feature").value = mediumInfo.feature_medium_id;
        container.querySelector("button.delete-feature").addEventListener("click", deleteFeature);

        return container.children[0];
    }

    #createBadge(content) {
        let newBadge = document.createElement("span");
        newBadge.classList.add("badge");
        newBadge.classList.add("rounded-pill");
        newBadge.classList.add("text-bg-primary");
        newBadge.classList.add("m-1");
        newBadge.innerHTML = content;
        return newBadge;
    }

    #htmlTemplate() {
        let html = `
        <div class="card shadow border-0 border border-primary m-3 d-flex p-3 pm-media"
            style="width: 20rem;">
            <div class="d-flex flex-wrap justify-content-between">
                <h5 class="medium-title"></h5>
                <div>
                    <button class="btn btn-white download-medium"><i data-feather="download"></i></button>
                    <button class="btn btn-white collapse-button" type="button" data-bs-toggle="collapse"
                    data-bs-target="" aria-expanded="false" aria-controls="collapseExample">
                        <i data-feather="info"></i>
                    </button>
                    <button class="btn btn-white delete-feature"><i data-feather="trash-2"></i></button>
                </div>
            </div>
            <img src="" class="card-img-top" alt="..."
                loading="lazy">
            <video src="" class="card-img-top" controls></video>
            <div class="badge-container my-1">
            </div>
            <div class="collapse my-1" id="">
                <div class="card card-body"></div>
            </div>
        </div>
        `
        return html;
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


class Page {
    constructor() {
        this.pageUl = document.getElementById("pagination");
        this.currentPage = document.getElementById("current_page");
        this.NUM_MEDIUM_PER_PAGE = 50;
    }

    initPages(media) {
        this.media = media;
        this.num_pages = Math.ceil(media.length / this.NUM_MEDIUM_PER_PAGE);


        this.pageUl.innerHTML = "";
        for (let i = 0; i < this.num_pages; i++) {
            var pageLi = this.pageTemplate(i, i == 0);
            pageLi.children[0].addEventListener("click", event => {
                this.directTo(event.currentTarget.value);
            });
            this.pageUl.appendChild(pageLi);
        }
    }

    pageTemplate(page, isActived) {
        var activeTag = "";
        if (isActived) {
            var activeTag = " active";
        }
        var template = `<li class="page-item${activeTag}"><button class="page-link" value=${page}>${page + 1}</button></li>`;
        let temp = document.createElement("div");
        temp.innerHTML = template;
        return temp.children[0];
    }

    directTo(page) {
        page = parseInt(page);
        var startPage = page * this.NUM_MEDIUM_PER_PAGE;
        var endPage = Math.min(this.media.length, (page + 1) * this.NUM_MEDIUM_PER_PAGE);

        mediaContainer.innerHTML = "";
        for (let i = startPage; i < endPage; i++) {
            let medium = mediumManager.createElement(this.media[i]);
            mediaContainer.appendChild(medium);
        }
        this.currentPage.innerHTML = page + 1;
        this.directStyle(page);
        feather.replace();
    }

    directStyle(page) {
        for (let page = 0; page < this.num_pages; page++) {
            this.pageUl.childNodes.forEach(element => {
                element.classList.remove("active");
            })
        }
        this.pageUl.childNodes[page].classList.add("active");
    }
}

var startDate = document.getElementById("start_date");
var endDate = document.getElementById("end_date");
var species = document.getElementById("species");
var behavior = document.getElementById("behavior");
var perchMount = document.getElementById("perch_mount_names")
var mediaContainer = document.getElementById("media_container");
var xhr = new XMLHttpRequest();
var mediumManager = new Medium();
var pagination = new Page();

function getConditions() {
    var selectedSpecies = [];
    var selectedBehavors = [];
    var selectedPerchMount = [];

    for (let sp of species) {
        if (sp.selected) {
            selectedSpecies.push(sp.value);
        }
    }

    for (let option of behavior.children) {
        if (option.selected) {
            selectedBehavors.push(option.value);
        }
    }

    for (let option of perchMount.children) {
        if (option.selected) {
            selectedPerchMount.push(option.value);
        }
    }


    return {
        "start_date": startDate.value,
        "end_date": endDate.value,
        "species": selectedSpecies,
        "behaviors": selectedBehavors,
        "perch_mount_name": selectedPerchMount,
    }
}


document.getElementById("search").addEventListener("click", event => {
    var condition = getConditions()

    xhr.open("post", "/feature_media", true)
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(condition))
    xhr.onload = function () {
        if (xhr.status == 200) {
            var results = JSON.parse(xhr.responseText)
            mediaContainer.innerHTML = "";
            pagination.initPages(results);
            pagination.directTo(0);
            // for (let mediumInfo of results) {
            //     let medium = mediumManager.createElement(mediumInfo);
            //     mediaContainer.appendChild(medium);
            // }
            // feather.replace();
        }
    }
});

document.getElementById("imageSizeRange").addEventListener("input", event => {
    var media = document.getElementsByClassName("pm-media");
    for (let medium of media) {
        medium.style.width = `${event.target.value}rem`
    }
})


function downloadMedium(event) {
    let objectId = event.currentTarget.value;
    location.href = `/download_medium/${objectId}`;
}

function deleteFeature(event) {
    var confirm = window.confirm("確定要刪除這個精選嗎？");
    var featureId = event.currentTarget.value;
    if (confirm) {
        xhr.open("delete", `/featured/${featureId}`, true)
        xhr.send();
        xhr.onload = function () {
            if (xhr.status != 200) {
                window.alert("刪除失敗！");
            } else {
                document.getElementById(`${featureId}`).remove();
                window.alert("刪除成功！");
            }

        }
    }
}