const reviewButton = document.getElementById("review_button")
const emptyCheckButton = document.getElementById("empty_check_button")
const reviewCover = document.getElementById("review-cover")
const emptyCheckCover = document.getElementById("empty-check-cover")
var perchMountName = document.getElementById("perch_mount_name")
var checkDate = document.getElementById("check_date")
var startDatetime = document.getElementById("start_datetime")
var endDatetime = document.getElementById("end_datetime")


reviewCover.addEventListener("click", function () {
    reviewButton.hidden = false
    emptyCheckButton.hidden = true
    perchMountName.value = ""
    startDatetime.value = ""
    endDatetime.value = ""
})

emptyCheckCover.addEventListener("click", function () {
    reviewButton.hidden = true
    emptyCheckButton.hidden = false
    perchMountName.value = ""
    startDatetime.value = ""
    endDatetime.value = ""
})

reviewButton.addEventListener("click", function (event) {
    var perchMountName = document.getElementById("perch_mount_name").value
    var startDatetimeValue = startDatetime.value
    var endDatetimeValue = endDatetime.value

    if (startDatetimeValue == "") {
        startDatetimeValue = `2000-01-01`
    }
    if (endDatetimeValue == "") {
        endDatetimeValue = `2050-12-31`
    }

    if (perchMountName == "") {
        alert("請輸入棲架名稱")
    } else {
        location.href = `/review/${perchMountName}/${startDatetimeValue} 00:00:00/${endDatetimeValue} 23:59:59`
    }
}
)

emptyCheckButton.addEventListener("click", function (event) {
    var perchMountName = document.getElementById("perch_mount_name").value
    var startDatetimeValue = startDatetime.value
    var endDatetimeValue = endDatetime.value

    if (startDatetimeValue == "") {
        startDatetimeValue = "any"
    }
    if (endDatetimeValue == "") {
        endDatetimeValue = "any"
    }

    if (perchMountName == "") {
        alert("請輸入棲架名稱")
    } else {
        location.href = `/empty_check/${perchMountName}/${startDatetimeValue}/${endDatetimeValue}`
    }
}
)