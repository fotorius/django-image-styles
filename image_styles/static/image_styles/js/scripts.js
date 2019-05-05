/* AJAX CSRF Support */
// https://docs.djangoproject.com/en/1.8/ref/csrf/
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


// https://docs.djangoproject.com/en/1.7/ref/contrib/csrf/
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');



$('.sortable').sortable({
  handle: '.effect-move',
  stop: function( event, ui ) {
    var weight=0;
    $(this).parent().find('form #id_weight').each(function(){
      $(this).val(weight);
      weight++;
    });
    $(this).parent().find('form .effect-save').trigger( "click" );
    $(this).find('.effect').addClass('moved');
  }
});

$('.effect-edit').on('click',function(){
  let form = $(this).closest('.effect').find('form');
  let attr = form.attr('hidden');
  if(typeof attr !== typeof undefined && attr !== false){
    form.removeAttr('hidden');
  }else{
    form.attr('hidden',true);
  }
});

var submit_name = '';
$('input[type="submit"]').click(function(e){
  e.preventDefault();
  submit_name = ($(this).attr('name')) ? $(this).attr('name') : '';
  $(this).closest('form').submit();
});

$(".effect-form").submit(function( event ) {
  event.preventDefault();
  var effect = $(this).closest('.effect');
  var effects = effect.closest('.effects');
  var loading = $('.loading');
  var method = submit_name == 'delete' ? 'DELETE' : 'POST';
  var url = $(this).attr('action');
  submit_name = '';
  loading.addClass('active');
  $.ajax({ 
    data: $(this).serialize(),
    method: method,
    url: url, 
    success: function(response) {
      effect.removeClass('moved');
      if(!$('.effect.moved').length) loading.removeClass('active');
      if(method == 'DELETE'){
        effect.remove();
      }else{
        $(this).html(response);
        $(this).find('input[type=submit]').click(function(e){
          e.preventDefault();
          submit_name = ($(this).attr('name')) ? $(this).attr('name') : '';
          $(this).closest('form').submit();
        });
      }
    }
  });
});

function format_modal_form(){
  $('#generic-modal form input[type=text]').addClass("form-control");
  $('#generic-modal form input[type=number]').addClass("form-control");
  $('#generic-modal form select').addClass("form-control");
  $('#generic-modal form input[type=submit]').click(function(e){
    e.preventDefault();
    submit_name = ($(this).attr('name')) ? $(this).attr('name') : '';
    $(this).closest('form').submit();
  });
  $('#generic-modal').modal('show');
  $("#generic-modal form").submit(function(event) {
    event.preventDefault();
    var method = submit_name == 'delete' ? 'DELETE' : 'POST';
    submit_name = '';
    $.ajax({
      method: method,
      data: $(this).serialize(),
      url: $(this).attr('action'), 
      success: function(response,status,xhr) {
        $('#generic-modal .modal-dialog').html(response);
        $('#generic-modal form input[type=text]').addClass("form-control");
        $('#generic-modal form input[type=number]').addClass("form-control");
        $('#generic-modal form select').addClass("form-control");
        if(!$('#generic-modal .modal-dialog form').length){
          location.reload();
        }else{
          format_modal_form(); 
        }
      }
    });
  });
}
$('[data-toggle="modal"]').on('click', function(e){
  e.preventDefault();
  let target = $($(this).data('target'));
  target.removeData('bs.modal');
  target.find('.modal-dialog').load($(this).attr('href'),function(response, status, xhr){
    format_modal_form(); 
  });
});

