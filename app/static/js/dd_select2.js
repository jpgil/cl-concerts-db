var dropsdowns=document.getElementsByClassName("dd_select2")
for (var i = 0; i < dropsdowns.length; i++) {
    $(dropsdowns[i]).select2({
      placeholder: 'Seleccionar - '+  dropsdowns[i].getAttribute('description'),
      width : '192px',
      ajax: {
        url: '/list/'+dropsdowns[i].getAttribute('url'),
        dataType: 'json',
        delay: 250,
        tags: true,
        data: function (params) {
          return {
            q: params.term, // search term
            page: params.page
          };
        },
        minimumInputLength: 1 ,
        processResults: function (data, params) {
          return { results: data.results, pagination: data.pagination };
        },
        cache: true
      },
      maximumSelectionLength: (dropsdowns[i].hasAttribute('maxelem')) ? parseInt(dropsdowns[i].getAttribute('maxelem')) : 1
    })
    
    selectedItems=dropsdowns[i].getAttribute('selectedElements').split(','); 
    var ddown=$(dropsdowns[i])
    for (var k = 0; k < selectedItems.length; k++) {    
        // Fetch the preselected item, and add to the control
        $.ajax({
            type: 'GET',
            url: '/list/'+dropsdowns[i].getAttribute('url')+'/'+selectedItems[k]
        }).then(function (data) {
        // create the option and append to Select2
        var option = new Option(data.text, data.id, true, true);      
        ddown.append(option).trigger('change');
        // manually trigger the `select2:select` event
        // $(dropsdowns[i]).trigger({  type: 'select2:select',  params: { data: data }  } );
        });
    }
    //$(dropsdowns[i]).select2("val",dropsdowns[i].getAttribute('selectedElements').split(','));    
}
