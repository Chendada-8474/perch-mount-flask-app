document.addEventListener("DOMContentLoaded", () => {
    var editMemberButtons = document.getElementsByClassName("edit-member");
    var editModalPosition = document.getElementById("editPosition");
    var editModalEmail = document.getElementById("editEmail");
    var editModalAdmin = document.getElementById("editAdmin");
    var editModalMemberId = document.getElementById("editMemberId");
    var sendDataButton = document.getElementById("send_data");
    var xhr = new XMLHttpRequest();


    for (let button of editMemberButtons) {
        button.addEventListener("click", updateEditUser)
    }

    function updateEditUser(event) {
        editModalPosition.value = event.currentTarget.querySelector("input[name='position_id']").value;
        editModalEmail.value = event.currentTarget.querySelector("input[name='email']").value;
        editModalAdmin.checked = event.currentTarget.querySelector("input[name='admin']").checked;
        editModalMemberId.value = event.currentTarget.querySelector("input[name='user_id']").value;
    }

    sendDataButton.addEventListener("click", event => {
        var email = editModalEmail.value;
        if (email == "None") {
            email = null;
        }
        data = {
            "email": email,
            "admin": editModalAdmin.checked,
            "position_id": editModalPosition.value,
        }
        console.log(editModalMemberId.value);
        xhr.open("post", `/user/${editModalMemberId.value}`, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(data));
        xhr.onload = function () {
            if (xhr.status == 200) {
                location.reload();
            }
        };
    })
})