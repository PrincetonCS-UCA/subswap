// get the modal body
// inject checkboxes
// verify checkboxes
// send swap request

var modal_buttons = document.getElementsByTagName("button"),
    len = modal_buttons.length,
    i;

function modalButtonClick() {
    var base_url = window.location.origin;
    // Get date of shift
    let requestid = $(this).data('requestid')
    console.log("Here:" + requestid)
    requestid = encodeURIComponent(requestid)
    var swap_options = document.getElementById("swap_modal_body_" + requestid);
    console.log(swap_options);
    // show list of possible shifts
    fetch(base_url + '/swap_shifts/' + requestid).then(function (response) {
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

for (i = 0; i < len; i += 1) {
    if (modal_buttons[i].hasAttribute("data-requestid")) {
        modal_buttons[i].onclick = modalButtonClick;
    }
}


// swap with selected request on submit
function swap_request(requestid) {
    // get swap_shift_data
    var swap_shift_data = document.querySelector('input[name="swap_shift_option"]:checked');
    if (swap_shift_data) {
        swap_shift_data = swap_shift_data.value;
        let requestId = encodeURIComponent(requestid)
        swap_shift_data = encodeURIComponent(swap_shift_data)
        let url = '/request/' + requestId + '/swap?swap_shift_data=' + swap_shift_data

        let _ = $.ajax({
            type: 'POST',
            url: url,
            success: function () {
                location.reload();
            }
        })
    } else {
        alert("Please choose a shift before submitting.")
    }
}
