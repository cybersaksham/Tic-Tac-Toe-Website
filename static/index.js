function showError($id, $msg){
    $($id).empty();
    $($id).append($msg);
}

$(document).ready(function(){
    // Pressing create room
    $('#createRoom').click(function(e){
        e.preventDefault();
        if($('#createName').val().length < 4 ||
        $('#createName').val().length > 10){
            showError('#errorTextCreate', "Name must be between 4 & 10 characters");
        }
        else{
            showError('#errorTextCreate', "")
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
            showError('#errorTextJoin', "")
        }
    });
});