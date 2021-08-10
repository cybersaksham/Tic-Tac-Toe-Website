function showError($msg){
    $('#errorText').empty();
    $('#errorText').append($msg);
}

$(document).ready(function(){
    $boxes = $('.gameBoxes');
    $url = window.location.href.split("/");
    $.each($boxes, function(index, value){
        $(value).click(function(e){
            e.preventDefault();
            showError("");
            $.ajax({
                url: 'clickBox?index='+index+'&room='+$url[$url.length - 1],
                method: "POST",
                success: function(res){
                    if(res["error"] != null){
                        showError(res["error"]);
                    }
                },
            });
        });
    });
});