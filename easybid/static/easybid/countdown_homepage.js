var count = document.getElementById("auction_count").innerHTML;
count = count.split(",");

function timedown(id){
    // Set the date we're counting down to
    var date = document.getElementById("end_time_"+id).innerHTML;
    var countDownDate =  new Date(date).getTime();
    var start_date =  new Date(document.getElementById("start_time_"+id).innerHTML).getTime();
    
    // Update the count down every 1 second
    var x = setInterval(function() {
    
      // Get today's date and time
      var now = new Date().getTime();

      if (start_date-now > 0){
        var distance = start_date-now;
        // Time calculations for days, hours, minutes and seconds
        var days = Math.floor(distance / (1000 * 60 * 60 * 24));
        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);
      
        // Display the result in the element with id="demo"
        document.getElementById("countdown_"+id).innerHTML = "Start in "+days + "d " + hours + "h "
        + minutes + "m " + seconds + "s ";
        document.getElementById("countdown_"+id).style.color = "#4289D7";
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
        document.getElementById("countdown_"+id).innerHTML = days + "d " + hours + "h "
        + minutes + "m " + seconds + "s left";
        document.getElementById("countdown_"+id).style.color = "#F07726";
      
        // If the count down is finished, write some text
        if (distance < 0) {
          clearInterval(x);
          document.getElementById("countdown_"+id).innerHTML = "EXPIRED";
          document.getElementById("countdown_"+id).style.color = "#3F3F3F";
        }
      }
    }, 1000);
}
var i;
for (i = 0; i < count.length; i++) {
    timedown(count[i]);
}