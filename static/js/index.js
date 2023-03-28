const reviewButton = document.getElementById("review_button")


reviewButton.addEventListener("click", function (event) {
    var perchMountName = document.getElementById("perch_mount_name").value
    var checkDate = document.getElementById("check_date").value
    if (perchMountName == "" || checkDate == "") {
        alert("請輸入棲架名稱或檢查日期")
    } else {
        console.log(perchMountName, checkDate);
        // location.href = `${perchMountName}/${checkDate}`
    }
}
)