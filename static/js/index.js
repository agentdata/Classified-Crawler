var taskId;
var uniqueId;
var statusInterval;

$(document).ready(function() {
    // this function called when the start crawler button is clicked
    $(document).on('click', '#start-crawl', function() {
        var url = ''
        var selection = $('#site-select option:selected').val();
        switch (selection) {
            case "1":
                url = 'https://offerup.com/search/?radius=30&delivery_param=p&sort=-posted&q='
                break
            case "2":
                url = 'https://saltlakecity.craigslist.org/search/sss?sort=date&query='
                break
        }

        collapseOrShowCrawlingProgress("show");
        // remove spaces and replace with %20 to be used in the URL
        var searchTerm = document.getElementById("searchTerm").value.split(' ').join('%20');
        $('#crawlingprogress').attr("class", "alert alert-secondary");
        $('#crawlingprogress').html('crawling...');
        $.ajax({
            url: '/api/crawl/',
            type: 'POST',
            data: {
                'url': url + searchTerm,
                'crawler': document.getElementById("site-select").value
            },
            success: crawlSuccess,
            error: crawlFail,
        })
    });
    $(document).on('click', '#show-existing', function() {
        collapseOrShowExistingProgress("show");
        $('#showexistingprogress').attr("class", "alert alert-secondary");
        $('#showexistingprogress').html('Getting existing entries from DB');
        $.ajax({
            url: '/api/showExisting/',
            type: 'GET',
            data: { 'show-searchTerm': document.getElementById("show-searchTerm").value },
            success: showExistingRecords,
            error: showExistingRecordsFail,
        })
    });
});

// submits a get call to the API with the given task and uniqueID to check the status
function checkCrawlStatus(taskId, uniqueId) {
    $.ajax({
        url: '/api/crawl/?task_id=' + taskId + '&unique_id=' + uniqueId + '/',
        type: 'GET',
        success: showCrawledData,
        error: showCrawledDataFail,
    })
}

// after a successful POST response this function starts a timed status check
function crawlSuccess(data) {
    document.getElementById("start-crawl").disabled = true;
    taskId = data.task_id;
    uniqueId = data.unique_id;
    statusInterval = setInterval(function() { checkCrawlStatus(taskId, uniqueId); }, 2000);
}

// after checkCrawlStatus get's a job completed response it calls this function to display the data on the web page.
function showCrawledData(data) {
    if (data.status) {
        $('#crawlingprogress').attr("class", "alert alert-secondary");
        $('#crawlingprogress').html('crawler is ' + data.status + ' ... ' + 'After crawling, the results are updated below');
    } else {
        clearInterval(statusInterval);
        document.getElementById("start-crawl").disabled = false;
        $("#crawlTable").html('<thead class="thead-dark"> <tr id="row-item"><th scope="col">Row#</th><th scope="col">Site</th><th scope="col">Title</th><th scope="col">Price</th><th scope="col">Date listed</th><th scope="col">URL</th></tr></thead><tbody id="crawlTableAdsList"></tbody>');

        $('#crawlingprogress').attr("class", "alert alert-primary");
        $('#crawlingprogress').html('crawling has finished!');

        var list = data.data;
        var html = '';
        for (var i = 0; i < list.length; i++) {
            html += `
            <tr>
                <th scope="row">` + (i + 1) + `</th>
                <td>` + getSite(list[i].adURL) + `</td>
                <td>` + list[i].Title + `</td>
                <td>$` + list[i].Price.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,') + `</td>
                <td>` + list[i].DateListed + `</td>
                <td width="20%"><a href="` + list[i].adURL + `">Link</td>
            </tr>
            `;
        }
        $('#crawlTableAdsList').html(html);
        setTimeout(() => collapseOrShowCrawlingProgress("hide"), 5000);
    }
}

function showExistingRecords(data) {
    clearInterval(statusInterval);
    document.getElementById("show-existing").disabled = false;
    $("#existingTable").html('<thead class="thead-dark"> <tr id="row-item"><th scope="col">Row#</th><th scope="col">Site</th><th scope="col">Title</th><th scope="col">Price</th><th scope="col">Date listed</th><th scope="col">URL</th></tr></thead><tbody id="existingTableAdsList"></tbody>');


    var list = data.data;
    var html = '';
    for (var i = 0; i < list.length; i++) {
        html += `
            <tr>
                <th scope="row">` + (i + 1) + `</th>
                <td>` + getSite(list[i].adURL) + `</td>
                <td>` + list[i].Title + `</td>
                <td>$` + list[i].Price.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,') + `</td>
                <td>` + list[i].DateListed + `</td>
                <td width="20%"><a href="` + list[i].adURL + `">Link</td>
            </tr>
            `;
    }
    $('#existingTableAdsList').html(html);
    $('#showexistingprogress').attr("class", "alert alert-primary");
    $('#showexistingprogress').html('Successfully pulled ' + Object.keys(list).length + ' items from the DB.');
    setTimeout(() => collapseOrShowExistingProgress("hide"), 5000);
}

function showExistingRecordsFail(data) {
    $('#showexistingprogress').html(data.responseJSON.error);
    $('#showexistingprogress').attr("class", "alert alert-danger");
    setTimeout(() => collapseOrShowExistingProgress("hide"), 5000);
}

// after a failed POST response this shows an error
function crawlFail(data) {
    $('#crawlingprogress').html(data.responseJSON.error);
    $('#crawlingprogress').attr("class", "alert alert-danger");

    clearInterval(statusInterval);
    setTimeout(() => collapseOrShowCrawlingProgress("hide"), 5000);
    document.getElementById("start-crawl").disabled = false;
}

function showCrawledDataFail(data) {
    $('#crawlingprogress').html(data.responseJSON.error);
    $('#crawlingprogress').attr("class", "alert alert-danger");

    clearInterval(statusInterval);
    setTimeout(() => collapseOrShowCrawlingProgress("hide"), 5000);
    document.getElementById("start-crawl").disabled = false;
}

function showDataFail(data) {
    $('#crawlingprogress').attr("class", "alert alert-danger");
    $('#crawlingprogress').html(data.responseJSON.error);
    $('#adsList').empty();

    clearInterval(statusInterval);
    setTimeout(() => collapseOrShowCrawlingProgress("hide"), 5000);
    document.getElementById("start-crawl").disabled = false;
}

// This function shows and hides the progress row
function collapseOrShowCrawlingProgress(choiceType) {
    if (choiceType === "hide") {
        document.getElementById("crawlingprogress").style.display = "none";
    } else if (choiceType === "show") {
        document.getElementById("crawlingprogress").style.display = "block";
    }
}
// This function shows and hides the progress row
function collapseOrShowExistingProgress(choiceType) {
    if (choiceType === "hide") {
        document.getElementById("showexistingprogress").style.display = "none";
    } else if (choiceType === "show") {
        document.getElementById("showexistingprogress").style.display = "block";
    }
}

// returns the originating site title
function getSite(url) {
    if (url.includes("craigslist")) {
        return 'craigslist';
    } else if (url.includes("offerup")) {
        return 'offerup';
    }
}

// This function adds the enter key press  while in the crawler search textbox to the start crawl button
$(document).ready(function() {
    $('#searchTerm').keypress(function(e) {
        if (e.keyCode == 13)
            $('#start-crawl').click();
    });
});

// This function adds the enter key press while in the textbox to the show-existing button
$(document).ready(function() {
    $('#show-searchTerm').keypress(function(e) {
        if (e.keyCode == 13)
            $('#show-existing').click();
    });
});