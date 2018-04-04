$(function() {
    $('.dropdown-button').dropdown();
    $('.button-collapse').sideNav();

    $('#update_hf').click(function(e){
       if ($('.hf:checked').length !== 3){
           e.preventDefault();
       }
    });
});