function timedown(){
    // Set the date we're counting down to
    var date = document.getElementById("end_time").innerHTML;
    var countDownDate = new Date(date).getTime();
    var start_date = new Date(document.getElementById("start_time").innerHTML).getTime();
    var btn = document.getElementById("bid_button");
    var edit_btn = document.getElementById("edit_button");
    var delete_btn = document.getElementById("delete_button");
    var now = new Date().getTime();
    if (btn != null){
        if(start_date- now > 0) btn.disabled = true;
        if(start_date- now <= 0) btn.disabled = false;
    } 

    if(edit_btn != null){
        if(start_date- now > 0) edit_btn.disabled = false;
        if(start_date- now <= 0) edit_btn.disabled = true;
    }
    if(delete_btn != null){
        if(start_date- now > 0) delete_btn.disabled = false;
        if(start_date- now <= 0) delete_btn.disabled = true;
    }

    // Update the count down every 1 second
    var x = setInterval(function() {
    
      // Get today's date and time
      now = new Date().getTime();

      if (start_date-now > 0){
        var distance = start_date-now;
        // Time calculations for days, hours, minutes and seconds
        var days = Math.floor(distance / (1000 * 60 * 60 * 24));
        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);
      
        // Display the result in the element with id="demo"
        document.getElementById("countdown").innerHTML = "Start in "+days + "d " + hours + "h "
        + minutes + "m " + seconds + "s ";

        document.getElementById("countdown").style.color = "#4289D7";
        if (btn != null){
            if(Math.floor((start_date - now)/1000) == 0) btn.disabled = false;
        }
        if (edit_btn != null){
            if(Math.floor((start_date - now)/1000) == 0) edit_btn.disabled = true;
        }
        if (delete_btn != null){
            if(Math.floor((start_date - now)/1000) == 0) delete_btn.disabled = true;
        }
      }
      else{

        // Find the distance between now and the count down date
        var distance = countDownDate - now;
        
        // Time calculations for days, hours, minutes and seconds
        var days = Math.floor(distance / (1000 * 60 * 60 * 24));
        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);
      
        // Display the result in the element with id="demo"
        document.getElementById("countdown").innerHTML = days + "d " + hours + "h "
        + minutes + "m " + seconds + "s left";
        document.getElementById("countdown").style.color = "#F07726";
      
        // If the count down is finished, write some text    
        if (distance < 0) {
          clearInterval(x);
          if (btn != null) btn.disabled = true;
          if (edit_btn != null) edit_btn.disabled = true;
          if (delete_btn != null) delete_btn.disabled = true;
          document.getElementById("countdown").innerHTML = "EXPIRED";
          document.getElementById("countdown").style.color = "#3F3F3F";
        }
      }
    }, 1000);
}

timedown();