

document.getElementById("project_filter").addEventListener("input", event => {
    var perch_mounts = document.getElementsByClassName("perch_mount");
    for (let pm of perch_mounts) {

        var project_id = pm.querySelector("input[name='project_id']").value;
        if (!event.target.value) {
            pm.style.display = "table-row"
            continue;
        }
        if (event.target.value == project_id) {
            pm.style.display = "table-row";
            continue;
        } else {
            pm.style.display = "none";
        }
    }
})

var addLayerButtons = document.getElementsByClassName("add-layer-modal");
for (let button of addLayerButtons) {
    button.addEventListener("click", event => {
        var perchMountName = event.currentTarget.querySelector("input[name='perch_mount_name']").value;
        var projectId = event.currentTarget.querySelector("input[name='project_id']").value;
        var habitatId = event.currentTarget.querySelector("input[name='habitat_id']").value;
        var latitude = event.currentTarget.querySelector("input[name='latitude']").value;
        var longitude = event.currentTarget.querySelector("input[name='longitude']").value;

        document.getElementById("layer_perch_mount_name").value = perchMountName;
        document.getElementById("layer_habitat_id").value = habitatId;
        document.getElementById("layer_project_id").value = projectId;
        document.getElementById("layer_latitude").value = latitude;
        document.getElementById("layer_longitude").value = longitude;

    })
}