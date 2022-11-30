let request_date = document.getElementById("date_requested")

request_date.onchange = function () {
    // show date error
    let date = request_date.value;
    console.log(date);
    if (new Date(date.replace(/-/g, '\/').replace(/T.+/, '')) < new Date()) {
        $("#daterror").html('<div class="alert alert-danger alert-dismissible fade show" role="alert"> \
    Please select a date starting tomorrow.\
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