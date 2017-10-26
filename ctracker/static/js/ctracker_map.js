
function fill_claim_form(org_id){
    $('#organization').val(org_id);
    for (var i = places.length - 1; i >= 0; i--) {
        if (places[i].data === parseInt(org_id)){
            $('#organization_name').val(places[i].value);
            $('#organization_name_div').text(places[i].value);
            break
        }
    }  
}    

function clear_claim_form(){
    $('#organization').val(null);
    $('#organization_name').val(null);    
}


function process_claim_template(template, data) {
    var message;
    if (data['bribe']) { message = template.replace('%bribe%', data['bribe']);}
    else { message = template.replace('%bribe%', '0');};

    message = message.replace('%broadcaster%', data['broadcaster_name']);
    message = message.replace('%servant%', data['servant']);
    message = message.replace('%text%', data['text']);
    message = message.replace('%created%', data['created']);

    if (data['claim_icon']) {
        message = message.replace('<div class="claim_icon"></div>',  
            '<div class="claim_icon"><img src="' + data['claim_icon'] + '"></div>');
    }

    return message;

}


function select_building (org_id, org_name, coordinates) {
    fill_claim_form(org_id);
    window.location.hash = "organization=" + org_id + "&zoom_to=" + coordinates; 

        $.ajax({
            type: "GET",
            url: api_url + 'claim/' + org_id + "/",
            success: function(data){
                var messages = "";
                var template, message

                template = document.getElementById('claim_template_for_org').innerHTML;

                var record;
                var count = 0;
                console.log(data);
                data = data['results']

                for (var i = data.length - 1; i >= 0; i--) {

                    if (count < 3) {
                        message = process_claim_template(template, data[i])

                        if (data[i]['complainer']) { 
                            var a_text = data[i]['complainer_name'] + ' (' + data[i]['complainer_count'] + ' ' + gettext("claims") + ')'
                            var onclick_args = data[i]['complainer']+','+ "'"+data[i]['complainer_name']+ "'"
                            var replace_str = '<a style="color:green;" id="' + data[i]['complainer'] + '" href="#" class="claims_of_user" onclick="get_claims_for_user('+ onclick_args +')">' + a_text +'</a>'
                            message = message.replace('%complainer%', replace_str);}

                        else { message = message.replace('%complainer%', gettext('Anon'));};
                        messages += message;
                        count += 1
                    } 
                }

                if (messages == "") {
                    messages = gettext('No claims for this organization');} 

                $("#claimsModal .modal-body").html(messages);
                $("#claimsModal .modal-title").html(org_name);          

                $("#claimsModal").modal("show");
                $(".navbar-collapse.in").collapse("hide");
            },
            error: function(data){
                console.log(data.responseText)
            }                
        });
}


function get_claims_for_user(user_id, username){
    $.ajax({
            type: "GET",
            url: api_url + 'claim/' + user_id + "/user/",
            success: function(data){
                var count = data.count;
                data = data['results'];                
                console.log(data, count);
                var messages = "";
                var template, message;

                template = document.getElementById('claim_template_for_user').innerHTML;          
            
                var count = 0               
                for (var i = data.length - 1; i >= 0; i--) {

                    if (count < 4) {
                        message = process_claim_template(template, data[i]);
                        message = message.replace('%organization%',  data[i]['organization_name']);
                       
                        messages += message;
                        count += 1
                    }                
                }
              
                $("#userclaimsModal .modal-body").html(messages);
                $("#userclaimsModal .modal-title").html(gettext('Claims from ')+ username);                              

                $("#claimsModal").modal("hide");
                $("#userclaimsModal").modal("show");
                $(".navbar-collapse.in").collapse("hide");                            
                        
            }, 
            error: function(data){
                console.log(data.responseText)
            }                
        });    
}



function add_claim(event){
    $('#processing').show();
    event.preventDefault();
    $.ajax({
        type: "POST",
        url: api_url + 'claim/',
        data: $('#claim_form').serialize(),
        statusCode: {
            200: function (response) {
                //
            },
            201: function (response) {
                //
            },
            400: function (response) {
                //
            },
            403: function (response) {
                alert(gettext("Too much claims. Please wait an hour and try again."));
            }
        },
        success: function(data){                 
            $('#processing').hide();
            // $('#message').html('Thank you for your message');
            window.location.reload();

            // $('#claim_text').val('');
            // $('#servant').val('');
            // if (grecaptcha_reset){
            //     grecaptcha.reset();
            // };
        },
        error: function(data){
            console.log(data.responseText)
        }                
    });
    return false;

}


function add_organization(event){
    $('#processing').show();
    event.preventDefault();
    post_data = $('#org_form').serialize();

    $.ajax({
        type: "POST",
        url: api_url + 'organization/',
        data: post_data,

        success: function(data){                 
            $('#processing').hide();
            var splitted_cntr = $('#centroid').val().split(',')
            window.location.hash = "organization=" + data.id + "&zoom_to=" + splitted_cntr[1]+','+splitted_cntr[0];                        
            window.location.reload();

        },
        error: function(data){
            console.log(data.responseText)
        }                
    });
    return false;

}



$(document).ready(function () {

    $("#back_button").click(function() {
      $("#userclaimsModal").modal("hide");
      $("#claimsModal").modal("show");
      $(".navbar-collapse.in").collapse("hide");
      return false;
    }); 

    $("#addclaim").click(function() {
      $("#claimsModal").modal("hide");
      $("#addclaimModal").modal("show");
      $(".navbar-collapse.in").collapse("hide");
      return false;
    });     


    $("#claim_form").submit(function(event){
        add_claim(event);
    });
    $("#org_form").submit(function(event){
        add_organization(event)
    });

    var csrftoken = $.cookie('csrftoken');
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#about-btn").click(function() {
      $("#aboutModal").modal("show");
      $(".navbar-collapse.in").collapse("hide");
      return false;
    });  


    $("#addorg-btn").click(function() {
      $("#addorgModal").modal("show");
      $(".navbar-collapse.in").collapse("hide");
      return false;
    });        

});




