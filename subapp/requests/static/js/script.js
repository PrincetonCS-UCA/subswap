var request_date = document.getElementById("date_requested");
var swap_options = document.getElementById("swap_options");
request_date.onchange = function () {
    // Get date of shift
    let date = request_date.value;
    if (new Date(date) < new Date()) {
        $("#daterror").html('<div class="alert alert-danger alert-dismissible fade show" role="alert"> \
        <strong>Hey!</strong> Please choose a valid date.\
        <button type="button" class="close" data-bs-dismiss="alert" aria-label="Close">\
        <span aria-hidden="true">&times;</span>\
        </button>\
        </div>');
    }
    date = encodeURIComponent(date);

    fetch('http://localhost:5000/swap_shifts/' + date).then(function (response) {
        response.json().then(function (data) {
            var optionHTML = '';

            for (let i = 0; i < data.swap_shifts.length; i++) {
                optionHTML += '<div class="form-check">';
                optionHTML += '<input class="form-check-input" name="swaps" type="checkbox" value="' + data.swap_shifts[i][0] + '">';
                optionHTML += '<label class="form-check-label" for="swaps-' + i + '">' + data.swap_shifts[i][1] + '</label>';
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