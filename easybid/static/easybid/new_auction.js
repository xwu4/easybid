$(document).ready( function() {
    $(document).on('change', '.btn-file :file', function() {
    var input = $(this),
        label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
    input.trigger('fileselect', [label]);
    });

    $('.btn-file :file').on('fileselect', function(event, label) {   
        var input = $(this).parents('.input-group').find(':text'),
            log = label;
        if( input.length ) {
            input.val(log);
        } else {
            if( log ) alert(log);
        }
    });
    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            
            reader.onload = function (e) {
                $('#product_image').attr('src', e.target.result);
            }
            
            reader.readAsDataURL(input.files[0]);
        }
    }
    $("#id_product_image").change(function(){
        readURL(this);
    }); 	
});

$(function () {
    $('#start_time').datetimepicker({
        minDate: new Date()
        
    });
    $('#end_time').datetimepicker({
        minDate: new Date()
    });
});

$('#start_time').on('change.datetimepicker', function() {
    var new_min_date = $(this).datetimepicker('date').add(1, "minutes");
    $("#end_time").datetimepicker('minDate', new_min_date);
});

