(function(){
    $('#input_site_domain').keyup(function(event) {
        // Ignore enter key
        if(event.which == 13) {
            event.preventDefault();
        }
        if ($(this).val() !== "") {
            var check_url = 'https://microco.sm/api/v1/reserved/' + $(this).val();
            $.getJSON(check_url, function(response) {
                console.log(response.reserved);
                if(response.reserved === true) {
                    $('#reserved-result').text("URL is already taken").css("color", "red")
                } else {
                    $('#reserved-result').text("URL is available").css("color", "green")
                }
            });
        } else {
            $('#reserved-result').text("")
        }
    });
})();
