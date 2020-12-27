const user_input = $("#user-input")
const search_icon = $('#search-icon')
const teachers_div = $('#replaceable-content')
const endpoint = '/home/'
const delay_by_in_ms = 500
let scheduled_function = false

console.log("Whats going on")

let ajax_call = function (endpoint, request_parameters) {
    $.getJSON(endpoint, request_parameters)
        .done(response => {
            console.log("Whats going on ajax call")
            // fade out the teachers_div, then:
            $('#replaceable-content').fadeTo('slow', 0).promise().then(() => {
                // replace the HTML contents
                $('#replaceable-content').html(response['html_from_view'])
                // fade-in the div with new contents
                $('#replaceable-content').fadeTo('slow', 1)
                // stop animating search icon
                $('#search-icon').removeClass('blink')
            })
        })
}

$("#user-input").on('keyup', function () {
    console.log("Whats going on")
    const request_parameters = {
        q: $(this).val() // value of user_input: the HTML element with ID user-input
    }
    console.log(request_parameters)
    // start animating the search icon with the CSS class
    $('#search-icon').addClass('blink')

    // if scheduled_function is NOT false, cancel the execution of the function
    if (scheduled_function) {
        clearTimeout(scheduled_function)
    }

    // setTimeout returns the ID of the function to be executed
    scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters)
})