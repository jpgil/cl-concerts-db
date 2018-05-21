var dropsdowns=document.getElementsByClassName("dd_select2")
for (var i = 0; i < dropsdowns.length; i++) {
    $(dropsdowns[i]).select2({
      placeholder: 'Seleccionar - '+  dropsdowns[i].getAttribute('description'),
      width : '192px',
      ajax: {
        url: '/list/'+dropsdowns[i].getAttribute('url'),
        dataType: 'json',
        delay: 250,
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
    });
}
