function showError($msg){
    $('#errorText').empty();
    $('#errorText').append($msg);
}

function showSuccess($msg){
    $('#successText').empty();
    $('#successText').append($msg);
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
            showSuccess("");
            $socket.emit('clickBox', $url[$url.length - 1], index);
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
        if(response.success != null){
            if(response.success == $playerID){
                showSuccess("Game over. You have won.");
            }
            else if(response.success == 0){
                showSuccess("Game over. No-one won.");
            }
            else{
                showSuccess("Game over. Opponent has won.");
            }
        }
    });

    $('#dltRoom').click(function(e){
        e.preventDefault();
        $socket.emit('dltRoom', $url[$url.length - 1])
    });
    $socket.on('room_deleted', function(response){
        $(location).attr('href', "/");
    });
});