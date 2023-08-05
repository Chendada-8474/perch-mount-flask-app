const emptyChart = echarts.init(document.getElementById('pending'));
// const detectedChart = echarts.init(document.getElementById('pending_detected'));
var trandButtons = document.getElementsByName("show_trand");
var request = new XMLHttpRequest();
var emptyCountTds = document.getElementsByClassName("empty-count");
var detectedCoTds = document.getElementsByClassName("detected-count");
var priorityChecks = document.getElementsByClassName("set-priority");
var claimChecks = document.getElementsByClassName("claim");
var memberId = document.getElementById("member_id");


for (let button of trandButtons) {
    button.addEventListener("click", requeryTrandData);
}

const MAXCOLORVALUE = 1000;
const COLORVALUERANGE = 150;
coloringTd(emptyCountTds, "blue")
coloringTd(detectedCoTds, "red")

function coloringTd(tds, color) {
    for (var td of tds) {
        var count = parseInt(td.innerText)

        var range = Math.round(count / MAXCOLORVALUE * (COLORVALUERANGE))

        if (color == "red") {
            td.style.backgroundColor = `rgb(255, ${255 - range}, ${255 - range})`
        } else if (color == "blue") {
            td.style.backgroundColor = `rgb(${255 - range}, ${255 - range}, 255)`
        }
    }
}

document.getElementById("project_filter").addEventListener("input", event => {
    var perch_mounts = document.querySelectorAll("tbody > tr");
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
    console.log(event.target.value)
})


for (let claim of claimChecks) {
    claim.addEventListener("click", claimPerchMount);
}

for (let priority of priorityChecks) {
    priority.addEventListener("click", setPerchMountPriority)
}

function claimPerchMount(event) {
    if (!event.target.checked) {
        request.open("delete", `/claim_perch_mount/${event.target.value}/${memberId.value}`)
    } else {
        request.open("post", `/claim_perch_mount/${event.target.value}/${memberId.value}`)
    }
    request.send();
    location.reload();
}

function setPerchMountPriority(event) {
    console.log(event.target.value, event.target.checked);
    if (event.target.checked) {
        request.open("post", `/perch_mount_priority/${event.target.value}/${1}`)
    } else {
        request.open("post", `/perch_mount_priority/${event.target.value}/${0}`)
    }
    request.send();
    location.reload();
}

function requeryTrandData(event) {
    var perch_mount_id = event.currentTarget.value;
    console.log(perch_mount_id)
    request.open("get", `/pending_media/${perch_mount_id}`, true);
    request.send();
    request.onload = function () {
        var results = JSON.parse(request.responseText);
        console.log(results)
        var detectedDateList = results.detected_seq.map(function (item) {
            return item[0];
        });
        var detectedValueList = results.detected_seq.map(function (item) {
            return item[1];
        });
        var emptyDateList = results.empty_seq.map(function (item) {
            return item[0];
        });
        var emptyValueList = results.empty_seq.map(function (item) {
            return item[1];
        });

        var option = {
            // Make gradient line here
            visualMap: [
                {
                    show: false,
                    type: 'continuous',
                    seriesIndex: 0,
                    min: 0,
                },
                {
                    show: false,
                    type: 'continuous',
                    seriesIndex: 0,
                    min: 0,
                    max: 400
                }
            ],
            title: [
                {
                    left: 'center',
                    text: '等待空拍檢查檔案數量'
                },
                {
                    top: '55%',
                    left: 'center',
                    text: '等待辨識物種檔案數量'
                }
            ],
            tooltip: {
                trigger: 'axis'
            },
            xAxis: [
                {
                    data: emptyDateList,
                },
                {
                    data: detectedDateList,
                    gridIndex: 1
                }
            ],
            yAxis: [
                {},
                {
                    gridIndex: 1
                }
            ],
            grid: [
                {
                    bottom: '60%'
                },
                {
                    top: '60%'
                }
            ],
            series: [
                {
                    type: 'line',
                    showSymbol: false,
                    data: emptyValueList,
                    lineStyle: {
                        normal: {
                            width: 4,
                        }
                    }
                },
                {
                    type: 'line',
                    showSymbol: false,
                    data: detectedValueList,
                    xAxisIndex: 1,
                    yAxisIndex: 1,
                    lineStyle: {
                        normal: {
                            width: 4,
                        }
                    }
                }
            ]
        };

        emptyChart.setOption(option)
        // detectedChart.setOption(option)

    }


}