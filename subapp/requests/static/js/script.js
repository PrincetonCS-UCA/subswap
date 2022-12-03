let request_date = document.getElementById("date_requested")


let valid_date = false;
request_date.onchange = function () {
    // get date entered by user
    let date = request_date.value;

    // get day of shift from metadata
    let day = document.getElementById("day-data").dataset.day;

    // check if date is in the future AND that it is on the day of the shift
    if (new Date(date) < new Date()) {
        $("#date_error").html('Please select a date starting tomorrow.');
        $("#form_error").html('');
        var base_price = document.getElementById("base_price");
        base_price.innerHTML = "Enter a valid date to calculate base price."
    } else if (getDayOfDate(date) != day) {
        $("#date_error").html('Please select a valid date. This one is not a ' + day + '.');
        $("#form_error").html('');
        var base_price = document.getElementById("base_price");
        base_price.innerHTML = "Enter a valid date to calculate base price."
    } else {
        $("#date_error").html('')
        valid_date = true;
        date = encodeURIComponent(date);

        // getting price
        let shiftid = window.location.href.split('/');
        shiftid = shiftid[shiftid.length - 2];
        var base_price = document.getElementById("base_price");
        fetch('http://localhost:5000/calculate_base_price?shiftid=' + shiftid + '&date=' + date).then(function (response) {
            response.json().then(function (data) {
                if (data.status == "True") {
                    base_price.innerHTML = data.price
                } else {
                    base_price.innerHTML = "You do not have sufficient credits to create this request. Please select another day or contact the Lab Manager."
                }
            })
        })
    }
}

//==============================================================================
// Helper functions
//==============================================================================

function getDayOfDate(date) {
    date = new Date(date.replace(/-/g, '\/').replace(/T.+/, ''));
    // Create an array of day names
    var dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

    // Use the getDay() method to get the day number (0-6)
    var dayNumber = date.getDay();

    // Return the name of the day, using the day number
    return dayNames[dayNumber];
}