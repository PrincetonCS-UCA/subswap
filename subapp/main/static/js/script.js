// get the modal body
// inject checkboxes
// verify checkboxes
// send swap request

var modal_button = document.getElementById("swap_modal_button");
var swap_options = document.getElementById("swap_modal_body");
modal_button.onclick = function () {
    swap_options.innerHTML = '';
    // Get date of shift
    let requestid = $(this).data('requestid')
    requestid = encodeURIComponent(requestid)

    // show list of possible shifts
    fetch('http://localhost:5000/swap_shifts/' + requestid).then(function (response) {
        response.json().then(function (data) {
            var optionHTML = '';

            for (let i = 0; i < data.swap_shifts.length; i++) {
                optionHTML += '<div class="form-check">';
                optionHTML += '<label>';
                optionHTML += '<input class="form-check-input" name="swap_shift_option" type="checkbox" value="' + data.swap_shifts[i][0] + ', ' + data.swap_shifts[i][1] + '">';
                optionHTML += data.swap_shifts[i][1] + '</label>'
                optionHTML += '</div>'
            }
            swap_options.innerHTML = optionHTML;

        })
    });
}


// swap with selected request on submit
function swap_request(requestid) {
    // get swap_shift_data
    var swap_shift_data = document.querySelector('input[name="swap_shift_option"]:checked').value;
    if (swap_shift_data) {
        let requestId = encodeURIComponent(requestid)
        swap_shift_data = encodeURIComponent(swap_shift_data)
        let url = '/request/' + requestId + '/swap' + '?swap_shift_data=' + swap_shift_data

        let _ = $.ajax({
            type: 'POST',
            url: url,
            success: function (response) {
                window.location.href = response.redirect_url;
            }
        })
    } else {
        alert("Please choose a shift before submitting.")
    }
}
