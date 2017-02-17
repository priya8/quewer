$(function(){

 $('#tags').keyup(function(){

  $.ajax({
     type:"POST",
     url:"/logtag/",
     data:{
        'search_text' : $('#ques').val(),
        'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
     },
     success:searchSuccess,
     dataType:'html'

  });
 });
});

function searchSuccess(data, testStatus ,jqXHR)
{
  $('$search-results').html(data);
}