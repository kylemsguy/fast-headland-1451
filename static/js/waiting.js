var ellipsisState = 1;
var ellipsisLimit = 5;
//var ellipsisHandle;
var ajaxHandle;

function advanceEllipsis() {
    console.log("advanceEllipsis: Running");
    $("#ellipsis").text(Array(ellipsisState).join("."));
    if(ellipsisState > ellipsisLimit){
        ellipsisState = 2;
    } else {
        ellipsisState++;
    }
}

function sendRequest() {
    console.log("Sending request to server...");
    var uuid = $("#uuid").attr("value");
    $.ajax({
       url: "/status/",
        data: { "uuid": uuid },
        beforeSend: advanceEllipsis,
        success: verifySuccess,
        error: function (jqXHR, textStatus, errorThrown){
            console.log(textStatus);
        }
    });
}

function verifySuccess(retobj){
    console.log(retobj);
    if(retobj.status == 2){
        // success
        clearInterval(ajaxHandle);
        //clearInterval(ellipsisHandle);
        $("#loading").html("Success! Get your file at this link: <a href=\"" + retobj.url + "\">Download!</a>");
    } else if (retobj.status == -1) {
        // invalid file
        clearInterval(ajaxHandle);
        $("#loading").html("Error: The file you uploaded is not a valid apk.");
    } else if (retobj.status == -2) {
        clearInterval(ajaxHandle);
        // Unknown Failure
        $("#loading").html("An unknown error occurred. Please try again later.");
    }
        // else still processing.

}

$(function(){
    console.log("Window loaded!");
    //ellipsisHandle = setInterval(advanceEllipsis, 1000);
    // fire off ajax requests
    ajaxHandle = setInterval(sendRequest, 1000);
});

