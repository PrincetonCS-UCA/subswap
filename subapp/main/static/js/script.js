var request_date = document.getElementById("date_requested");
var swap_options = document.getElementById("swap_options");
request_date.onchange = function () {
    swap_options.innerHTML = '';
    // Get date of shift
    let date = request_date.value;
    if (new Date(date.replace(/-/g, '\/').replace(/T.+/, '')) < new Date()) {
        $("#daterror").html('<div class="alert alert-danger alert-dismissible fade show" role="alert"> \
        <strong>Hey!</strong> Please choose a valid date.\
        <button type="button" class="close" data-bs-dismiss="alert" aria-label="Close">\
        <span aria-hidden="true">&times;</span>\
        </button>\
        </div>');
    } else {
        $("#daterror").html('')
    }
    date = encodeURIComponent(date);

    // getting price
    let shiftid = window.location.href.split('/');
    shiftid = shiftid[shiftid.length - 2];
    var base_price = document.getElementById("base_price");
    fetch('http://localhost:5000/calculate_base_price/' + shiftid + '/' + date).then(function (response) {
        response.json().then(function (data) {
            if (data.status == "True") {
                base_price.innerHTML = data.price
            } else {
                base_price.innerHTML = "You do not have sufficient credits to create this request. Please select another day or contact the Lab Manager."
            }
        })
    })

    fetch('http://localhost:5000/swap_shifts/' + date).then(function (response) {
        response.json().then(function (data) {
            var optionHTML = '';

            for (let i = 0; i < data.swap_shifts.length; i++) {
                optionHTML += '<div class="form-check">';
                optionHTML += '<label>';
                optionHTML += '<input class="form-check-input" name="swaps" type="checkbox" value="' + data.swap_shifts[i][0] + ', ' + data.swap_shifts[i][1] + '">';
                optionHTML += data.swap_shifts[i][1] + '</label>'
                optionHTML += '</div>'
            }
            swap_options.innerHTML = optionHTML;

        })
    });
}

var swap_form = document.getElementById("swapsubform");
$('input[type=radio][id=swap_toggle]').change(function () {
    if (this.value == "True") {
        if (request_date.value == '') {
            $("#daterror").html('<div class="alert alert-danger alert-dismissible fade show" role="alert"> \
            Please enter a date first.\
            <button type="button" class="close" data-bs-dismiss="alert" aria-label="Close">\
            <span aria-hidden="true">&times;</span>\
            </button>\
            </div>');
        } else {
            swap_form.style.display = '';
        }
    }
});