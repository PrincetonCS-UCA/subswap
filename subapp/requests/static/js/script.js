let request_date = document.getElementById("date_requested")
let base_url = window.location.origin;
let submit_button = document.getElementById("submit")
submit_button.disabled = true;

let valid_date = false;
let valid_bonus = false;

request_date.onchange = function () {
    valid_date = false;
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
            } else {
                base_price.innerHTML = "You do not have sufficient credits to create this request. Please select another day or contact the Lab Manager."
            }
        });
    }

    if (valid_date && valid_bonus) {
        submit_button.disabled = false;
    }
}

let bonus_price = document.getElementById("bonus")

bonus_price.onchange = async function () {
    valid_bonus = false;
    submit_button.disabled = true;
    let bonus = Number(bonus_price.value);
    let date = request_date.value;
    let response = await getBasePrice(date);
    let current_balance = await getBalance();

    if (!valid_date) {
        $("#date_error").html('Please select a valid date first.');
        $("#form_error").html('');
        var base_price = document.getElementById("base_price");
        base_price.innerHTML = "Enter a valid date to calculate base price."
    } else if (bonus < 0) {
        $("#bonus_error").html('Please enter a positive number.');
        $("#form_error").html('');
    } else if (response.price + bonus > current_balance) {
        $("#bonus_error").html('You do not have sufficient credits to add this bonus.');
        $("#form_error").html('');
    } else {
        valid_bonus = true;
        $("#bonus_error").html('');
        $("#form_error").html('');
    }
    if (valid_bonus && valid_date) {
        submit_button.disabled = false;
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

async function getBasePrice(date) {

    date = encodeURIComponent(date);

    // getting price
    let shiftid = window.location.href.split('/');
    shiftid = shiftid[shiftid.length - 2];
    var base_price = document.getElementById("base_price");
    const response = await fetch(base_url + '/calculate_base_price?shiftid=' + shiftid + '&date=' + date);
    return await response.json();
}

async function getBalance() {
    let res = await fetch(base_url + '/check_balance');
    let res_json = await res.json();
    return res_json.balance;
}