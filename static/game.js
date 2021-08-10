function showError($msg){
    $('#errorText').empty();
    $('#errorText').append($msg);
}

function updateHTMl($boxes, $playerID, $status, $turn){
    $.each($boxes, function(index, value){
        if($status[index] == "n"){
            $(value).text("-");
        }
        else{
            $(value).text($status[index]);
        }
    });
    $('#renderedTurn').hide();
    $('#jsTurn').show();
    $('#jsTurn').empty();
    if($turn == $playerID){
        $('#jsTurn').append("Your Turn");
    }
    else{
        $('#jsTurn').append("Opponent's Turn");
    }
}

$(document).ready(function(){
    $socket = io();
    $boxes = $('.gameBoxes');
    $url = window.location.href.split("/");
    $.each($boxes, function(index, value){
        $(value).click(function(e){
            e.preventDefault();
            showError("");
            $socket.emit('clickBox', $url[$url.length - 1], index);
//            $.ajax({
//                url: 'clickBox?index='+index+'&room='+$url[$url.length - 1],
//                method: "POST",
//                success: function(res){
//                    if(res["error"] != null){
//                        showError(res["error"]);
//                    }
//                },
//            });
        });
    });
    $socket.on('click_result', function(response){
        $playerID = $('#playerID').text().split(" ")[1];
        if(response.error != null){
            if(response.errorID == $playerID){
                showError(response.error);
            }
        }
        else{
            updateHTMl($boxes, $playerID, response.result, response.turn);
        }
    });
});