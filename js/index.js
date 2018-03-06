nboxes = 16;
strings = [];

$(function() {
    $('.dropdown-button').dropdown();

    for (var i=0; i<nboxes; i++) {
        $("#labels").append('<th id="label" i="' + i + '">' + i + '</th>');
        $("#bits").append('<td id="bit" i="' + i + '"></td>');
    }

});