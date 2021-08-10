// Function to show error
function showError($id, $msg){
    $($id).empty();
    $($id).append($msg);
}

// Starting Point
$(document).ready(function(){
    // Pressing create room
    $('#createRoom').click(function(e){
        e.preventDefault();
        if($('#createName').val().length < 4 ||
        $('#createName').val().length > 10){
            showError('#errorTextCreate', "Name must be between 4 & 10 characters");
        }
        else{
            showError('#errorTextCreate', "");
            $.ajax({
                url: '/create_room',
                method: 'POST',
                data: $('#createForm').serialize(),
                success: function(res){
                    if(res["error"] != null){
                        showError('#errorTextCreate', res["error"]);
                    }
                    else{
                        $(location).attr('href', "/" + res["id"]);
                    }
                },
                error: function(){
                    showError('#errorTextCreate', "Connection error. Try again.");
                }
            });
        }
    });

    // Pressing join room
    $('#joinRoom').click(function(e){
        e.preventDefault();
        if($('#joinName').val().length < 4 ||
        $('#joinName').val().length > 10){
            showError('#errorTextJoin', "Name must be between 4 & 10 characters");
        }
        else if($('#joinID').val() == ""){
            showError('#errorTextJoin', "Enter a room ID.");
        }
        else{
            showError('#errorTextJoin', "");
            $.ajax({
                url: '/join_room',
                method: 'POST',
                data: $('#joinForm').serialize(),
                success: function(res){
                    if(res["error"] != null){
                        showError('#errorTextJoin', res["error"]);
                    }
                    else{
                        $(location).attr('href', "/" + res["id"]);
                    }
                },
                error: function(){
                    showError('#errorTextJoin', "Connection error. Try again.");
                }
            });
        }
    });
});