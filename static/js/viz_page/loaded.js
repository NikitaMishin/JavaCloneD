
let dataFromServer  = undefined;



$(document).ready( ()=> {
  $.getJSON('/analysis_data/' + $(location).attr("href").split('/').pop(), function(data){
    dataFromServer = data;
  });
});
