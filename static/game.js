// Function to show error messages
function showError($msg){
    $('#flashMsg').empty();
    $('#flashMsg').append(
    "<div class=\"alert alert-danger alert-dismissible fade show\" role=\"alert\">"+
    "<strong>" + $msg + "</strong>"+
    "<button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"alert\""+
    "aria-label=\"Close\"></button>"+
    "</div>");
    setTimeout(function () {
        $('#flashMsg').empty();
    }, 3000)
}

// Function to show success messages
function showSuccess($msg){
    $('#flashMsg').empty();
    $('#flashMsg').append(
    "<div class=\"alert alert-success alert-dismissible fade show\" role=\"alert\">"+
    "<strong>" + $msg + "</strong>."+
    "<button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"alert\""+
    "aria-label=\"Close\"></button>"+
    "</div>");
    setTimeout(function () {
        $('#flashMsg').empty();
    }, 3000)
}

// Function to update HTML after socket response
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

// Starting Point
$(document).ready(function(){
    // Making Socket
    $socket = io(window.location.href + ':3000');

    // Initializing variables
    $boxes = $('.gameBoxes');
    $url = window.location.href.split("/");
    $playerID = $('#playerID').text().split(" ")[1];

    // Assigning js values
    $('#roomID').text("Room ID " + $url[$url.length - 1]);
	
	// On connecting
	$socket.on('connect', function(){
		$socket.emit('joinedRoom', $url[$url.length - 1], $playerID);
	});
	$socket.on('join_msg', function(response){
		if(response.roomID == $url[$url.length - 1]){
			if(response.msg != null){
				showSuccess(response.msg);
			}
		}
	});

    // Clicking on boxes
    $.each($boxes, function(index, value){
        $(value).click(function(e){
            e.preventDefault();
            $socket.emit('clickBox', $url[$url.length - 1], index);
        });
    });
    // Socket result of box clicking
    $socket.on('click_result', function(response){
        if(response.roomID == $url[$url.length - 1]){
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
					showError("Game over. Opponent has won.");
				}
			}
		}
    });

    // Pressing delete room button
    $('#dltRoom').click(function(e){
        e.preventDefault();
        $socket.emit('dltRoom', $url[$url.length - 1])
    });
    // Socket result of deleting room
    $socket.on('room_deleted', function(response){
		if(response.roomID == $url[$url.length - 1]){
			$(location).attr('href', "/");
		}
    });

    // Pressing restart game button
    $('#restartBtn').click(function(e){
        e.preventDefault();
        $socket.emit('restartGame', $url[$url.length - 1])
    });
    // Socket result of restarting game
    $socket.on('game_restarted', function(response){
		if(response.roomID == $url[$url.length - 1]){
			location.reload();
		}
    });

    // Pressing quit room button
    $('#quitRoom').click(function(e){
        e.preventDefault();
        $socket.emit('quitRoom', $url[$url.length - 1])
    });
    // Socket result of quitting room
    $socket.on('room_exited', function(response){
		if(response.roomID == $url[$url.length - 1]){
			if(response.id == $playerID){
				$(location).attr('href', "/");
			}
			else{
				showError(response.msg);
				updateHTMl($boxes, $playerID, "nnnnnnnnn", $playerID);
			}
		}
    });
});