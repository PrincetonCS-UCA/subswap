let request_date = document.getElementById("date_requested")
let base_url = window.location.origin;
let submit_button = document.getElementById("submit")
submit_button.disabled = true;

let valid_date = false;

request_date.onchange = function () {
    valid_date = false;
    // get date entered by user
    let date = request_date.value;

    // get day of shift from metadata
    let day = document.getElementById("day-data").dataset.day;

    // check if date is in the future AND that it is on the day of the shift
    if (!moment(date).isAfter(moment())) {
        $("#date_error").html('Please select a date starting tomorrow.');
        $("#form_error").html('');
        var base_price = document.getElementById("base_price");
        base_price.innerHTML = "Enter a valid date to calculate base price."
    } else if (moment(date).format('dddd') != day) {
        $("#date_error").html('Please select a date that falls on a ' + day + '.');
        $("#form_error").html('');
        var base_price = document.getElementById("base_price");
        base_price.innerHTML = "Enter a valid date to calculate base price."
    } else {
        $("#date_error").html('')
        valid_date = true;

        // getting price
        var base_price = document.getElementById("base_price");
        getBasePrice(date).then(response => {
            if (response.status == "True") {
                base_price.innerHTML = response.price
                submit_button.disabled = false;
            } else {
                base_price.innerHTML = "You do not have sufficient credits to create this request. Please select another day or contact the Lab Manager."
            }
        });
    }
}

//==============================================================================
// Helper functions
//==============================================================================

async function getBasePrice(date) {

    date = encodeURIComponent(date);

    // getting price
    let shiftid = window.location.href.split('/');
    shiftid = shiftid[shiftid.length - 2];
    var base_price = document.getElementById("base_price");
    const response = await fetch(base_url + '/calculate_base_price?shiftid=' + shiftid + '&date=' + date);
    return await response.json();
}
