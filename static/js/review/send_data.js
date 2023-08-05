function sendReview(submitButton) {
    var occurrences = [];
    var eventMedia = [];
    var emptyMediumIds = [];
    var featuredMedia = [];
    var media = document.getElementById("contents").children

    for (let medium of media) {
        var mediumInfo = extractMediumInfo(medium);
        if (mediumInfo.event_id) {
            eventMedia.push({
                "object_id": mediumInfo.object_id,
                "event_id": mediumInfo.event_id,
                "medium_datetime": mediumInfo.medium_datetime,
            });
        }

        var individuals = medium.querySelectorAll("tbody > tr");
        if (!individuals.length) {
            if (!mediumInfo.feature_behavior && !mediumInfo.event_id) {
                emptyMediumIds.push(mediumInfo.object_id);
            } else {
                featuredMedia.push({
                    "object_id": mediumInfo.object_id,
                    "title": mediumInfo.feature_title,
                    "description": mediumInfo.feature_description,
                    "behavior": mediumInfo.feature_behavior,
                    "medium_datetime": mediumInfo.medium_datetime,
                    "is_image": mediumInfo.is_image,
                    "species": null,
                });
            }
            continue;
        }

        for (let individual of individuals) {
            var individualInfo = extractIndividualInfo(individual);
            mediumInfo.individuals.push(individualInfo);
        }

        // delete mediumInfo.object_id;
        delete mediumInfo.event_id;


        if (mediumInfo.feature_behavior) {
            for (let individual of mediumInfo.individuals) {
                featuredMedia.push({
                    "object_id": mediumInfo.object_id,
                    "title": mediumInfo.feature_title,
                    "description": mediumInfo.feature_description,
                    "behavior": mediumInfo.feature_behavior,
                    "medium_datetime": mediumInfo.medium_datetime,
                    "is_image": mediumInfo.is_image,
                    "species": individual.common_name_by_human,
                    "featured_by": document.getElementById("current_user").value
                });
            }
        }

        delete mediumInfo.feature_title;
        delete mediumInfo.feature_behavior;
        delete mediumInfo.feature_description;

        occurrences.push(mediumInfo);
    }

    var data = {
        "occurrences": occurrences,
        "event_media": eventMedia,
        "empty_media_ids": emptyMediumIds,
        "featured_media": featuredMedia,
    }
    submitButton.value = JSON.stringify(data);
}

function extractMediumInfo(medium) {
    let info = {
        "object_id": medium.id,
        "medium_datetime": medium.querySelector("input[name='medium_datetime']").value,
        "is_image": medium.querySelector("input[name='is_image']").checked,
        "feature_title": medium.querySelector("input[name='feature_title']").value,
        "feature_behavior": medium.querySelector("input[name='feature_behavior']").value,
        "feature_description": medium.querySelector("input[name='feature_description']").value,
        "event_id": medium.querySelector("select[name='event']").value,
        "individuals": [],
    }
    return info;
}

function extractIndividualInfo(individual) {
    var aiCommonName = individual.querySelector("input[name='ai_species']").value;
    var humanCommonName = individual.querySelector("input[name='common_ch_name']").value;
    var ringNumber = individual.querySelector("input[name='ring_number']").value

    if (!humanCommonName) {
        humanCommonName = aiCommonName;
    }
    if (!ringNumber) {
        ringNumber = null;
    }

    let xmin = individual.querySelector("input[name='xmin']").value
    let xmax = individual.querySelector("input[name='xmax']").value
    let ymin = individual.querySelector("input[name='ymin']").value
    let ymax = individual.querySelector("input[name='ymax']").value
    if (!xmin) {
        xmin = null
    }
    if (!xmax) {
        xmax = null
    }
    if (!ymin) {
        ymin = null
    }
    if (!ymax) {
        ymax = null
    }

    info = {
        "xmin": xmin,
        "xmax": xmax,
        "ymin": ymin,
        "ymax": ymax,
        "common_name_by_ai": aiCommonName,
        "common_name_by_human": humanCommonName,
        "tagged": individual.querySelector("input[name='tagged']").checked,
        "prey": individual.querySelector("input[name='prey']").checked,
        "ring_number": ringNumber,
    }
    return info;
}

function extractFeatureInfo(medium) {
    let info = {
        "object_id": medium.id,
        "medium_datetime": medium.querySelector("input[name='medium_datetime']").value,
        "is_image": medium.querySelector("input[name='is_image']").checked,
        "feature_title": medium.querySelector("input[name='feature_title']").value,
        "feature_behavior": medium.querySelector("input[name='feature_behavior']").value,
        "feature_description": medium.querySelector("input[name='feature_description']").value,
    }
    return info;
}

function extractEventInfo(medium) {
    let info = {
        "object_id": medium.id,
        "medium_datetime": medium.querySelector("input[name='medium_datetime']").value,
        "event_id": medium.querySelector("select[name='event']").value,
    }
    return info;
}