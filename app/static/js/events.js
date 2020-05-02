function addParticipant(event_id) {
    var activity = document.getElementById("activity");
    var person = document.getElementById("person");
     if (person.selectedIndex == -1){
        flash("Debe seleccionar una persona","warning")
        return
    }
    activity_id = -1 
    if (activity.selectedIndex != -1){
        activity_id = parseInt(activity.options[activity.selectedIndex].value)
    }

    data = {
        'event_id' : event_id,
        'person_id' : parseInt(person.options[person.selectedIndex].value),
        'activity_id' : activity_id
    }
     
    $.post('/api/participant/add',data ).done( function(msg) { 
            $('#table-participants').bootstrapTable('refresh');
      }).fail( function(xhr, textStatus, errorThrown) {
        flash(xhr.responseText,"error");
    });
};

function deleteParticipantCol(value, row, index){
    return '<i class="glyphicon glyphicon-trash"  onclick="deleteParticipant('+value+')"></i>'           
}
function deleteParticipant(participant_id)
{
    $.post('/api/participant/delete', { 'participant_id':participant_id } ).done( function(msg) { 
            $('#table-participants').bootstrapTable('refresh');
            $('#table-performance-participant').bootstrapTable('refresh');
            $("#participant").val('').trigger('change');
            $("#performance").val('').trigger('change');
            
             } )
    .fail( function(xhr, textStatus, errorThrown) {
        flash(xhr.responseText,'error');
    });    
};



function deleteElement(model,id)
{
    $.post('/api/delete/'+model+'/'+id ).done( 
        function() {
            flash("Elemento eliminado exitosamente","info")
            $("#show-list-table").bootstrapTable('refresh');
            })
        .fail( 
           function(xhr, textStatus, errorThrown) {
             flash(xhr.responseText,'error');
          }  );
               
}


function checkDeleteElement(model,id)
{
    //deleteElementModal()
    $.post('/api/deletecheck/'+model+'/'+id  ).done( 
        function(data) { 
          if (data.hard_deps){
            BootstrapDialog.show(
            {
              message: data.hard_deps,
              buttons: [
                {
                  label: 'Cerrar',
                  action: function(dialogItself){
                            dialogItself.close();
                            }
                }
               ]
              });
             }  
            else if (data.soft_deps) {
            BootstrapDialog.show(
            {
              message: data.soft_deps,
              buttons: [
                {
                  label: 'Sí, eliminar',
                  cssClass: 'btn-primary',
                  action: function(dialogItself){
                           deleteElement(model,id)
                           dialogItself.close();
                          }
                },
                {
                  label: 'Cancelar',
                  action: function(dialogItself){
                          dialogItself.close();
                          }
                }
               ]
              });
             } else {
             no_deps_message='<h4>¿Está seguro que quiere eliminar este objeto?</h4>'
             if (model == 'Event' || model == 'MusicalEnsemble')
             {
                 no_deps_message=no_deps_message+'<br>Todos los archivos asociados serán eliminados'
             }
             BootstrapDialog.show(
             
            {
              message: no_deps_message,
              buttons: [
                {
                  label: 'Sí, eliminar',
                  cssClass: 'btn-primary',
                  action: function(dialogItself){
                           deleteElement(model,id)
                           dialogItself.close();
                          }
                },
                {
                  label: 'Cancelar',
                  action: function(dialogItself){
                          dialogItself.close();
                          }
                }
               ]
              });            
              
          
          }
       }
    ).fail( function(xhr, textStatus, errorThrown) {
        flash(xhr.responseText,'error');
    });    
}



function addMusicalEnsembleToEvent(event_id)
{
    var musical_ensemble = document.getElementById("musical_ensemble");
    if (musical_ensemble.selectedIndex == -1 ){
        flash("Debe seleccionar una agrupación musical","warning")
        return
    }   
    musical_ensemble_id = parseInt(musical_ensemble.options[musical_ensemble.selectedIndex].value)
    data = {
        'musical_ensemble_id' : musical_ensemble_id,
        'event_id' : event_id,
    }
    $.post('/api/musicalensembleatevent/add',data ).done( function(msg) { 
            $('#table-participants').bootstrapTable('refresh');
      }).fail( function(xhr, textStatus, errorThrown) {
        flash(xhr.responseText,"error");
    });        
}

function addMusicalEnsembleMember(musical_ensemble_id) {
    var activity = document.getElementById("activity");
    var person = document.getElementById("person");

    activity_id = -1 
    if (activity.selectedIndex != -1){
        activity_id = parseInt(activity.options[activity.selectedIndex].value)
    }
    person_id = -1
    if (person.selectedIndex != -1){
        person_id = parseInt(person.options[person.selectedIndex].value)
    }
    if (person.selectedIndex == -1 && activity.selectedIndex == -1){
        flash("Debe seleccionar una persona o actividad","warning")
        return
    }
    data = {
        'musical_ensemble_id' : musical_ensemble_id,
        'person_id' : person_id,
        'activity_id' : activity_id
    }
    $.post('/api/musicalensemblemember/add',data ).done( function(msg) { 
            $('#table-musical-ensemble-members').bootstrapTable('refresh');
      }).fail( function(xhr, textStatus, errorThrown) {
        flash(xhr.responseText,"error");
    });
};



function deleteMusicalEnsembleMemberCol(value, row, index){
    return '<i class="glyphicon glyphicon-trash"  onclick="deleteMusicalEnsembleMember('+value+')"></i>'           
}

function deleteMusicalEnsembleMemberCol(value, row, index){
    return '<i class="glyphicon glyphicon-trash"  onclick="checkDeleteMusicalEnsembleMember('+value+')"></i>'           
}

function checkDeleteMusicalEnsembleMember(musical_ensemble_member_id)
{

        $.ajax({
            type: 'GET',
            url: '/list/eventsofmember/'+musical_ensemble_member_id,
            async: false
        }).then(function (data) {
        // create the option and append to Select2
            if(data.events.length == 0){
                deleteMusicalEnsembleMember(musical_ensemble_member_id)    
            }
            else {
                console.log(data.events.length)
                $('#confirmDelete').find('.modal-body').html("<h3>Se borrará su participación de:</h3>");     
                for (ev_id in data.events){
                    $('#confirmDelete').find('.modal-body').append('<p>'+data.events[ev_id]+'</p>');
                 }
                 $('#confirmDelete').find('.modal-footer').html("");
                 $('#confirmDelete').find('.modal-footer').append('<button type="button" class="btn btn-default" data-dismiss="modal" onclick="javascript:deleteMusicalEnsembleMember('+musical_ensemble_member_id+')">Sí</button>')
                 $('#confirmDelete').find('.modal-footer').append('<button type="button" class="btn btn-default" data-dismiss="modal">No</button>')
                 $('#confirmDelete').modal()
            }

        });

}

function deleteMusicalEnsembleMember(musical_ensemble_member_id)
{
    $.post('/api/musicalensemblemember/delete', { 'musical_ensemble_member_id': musical_ensemble_member_id } ).done( function(msg) { 
            $('#table-musical-ensemble-members').bootstrapTable('refresh'); } )            
    .fail( function(xhr, textStatus, errorThrown) {
        flash(xhr.responseText,'error');
    });    
}



function addPerformance(event_id) {
    var musical_piece = document.getElementById("musical_piece");
    var premiere_type = document.getElementById("premiere_type");
     if (musical_piece.selectedIndex == -1){
        flash("Debe seleccionar una obra","warning")
        return
    }
    if (premiere_type.selectedIndex == -1){
        flash("Debe seleccionar un tipo de estreno","warning")
        return
    }
    data = {
        'event_id' : event_id,
        'musical_piece_id' : parseInt(musical_piece.options[musical_piece.selectedIndex].value),
        'premiere_type_id' : parseInt(premiere_type.options[premiere_type.selectedIndex].value)
    }
     
    $.post('/api/performance/add',data ).done( function(msg) { 
             $('#table-musical-pieces').bootstrapTable('refresh'); } )
    .fail( function(xhr, textStatus, errorThrown) {
        flash(xhr.responseText,"error");
    });
}

function deletePerformanceCol(value, row, index){
    return '<i class="glyphicon glyphicon-trash"  onclick="deletePerformance('+value+')"></i>'           
}

function deletePerformance(performance_id)
{
    $.post('/api/performance/delete', { 'performance_id':performance_id } ).done( function(msg) { 
            $('#table-musical-pieces').bootstrapTable('refresh');
            $('#table-performance-participant').bootstrapTable('refresh');
            $("#participant").val('').trigger('change');
            $("#performance").val('').trigger('change');
             } )
    .fail( function(xhr, textStatus, errorThrown) {
        flash(xhr.responseText,"error");
    });    
}

function mergeRows(table_name, field_name,index, rowspan) {
    $('#'+table_name).bootstrapTable('mergeCells', {
        index: index,
        field: field_name,
        rowspan: rowspan
    });
}


function mergeTable(table_name,field_name) {
    var table = document.getElementById(table_name);
    var rowLength = table.rows.length;
    var count = 0;
    var row = table.rows[1].cells[0].innerHTML;
    var saveIndex = 0;

        for (var i = 1; i < rowLength; i++) {        
        if (row === table.rows[i].cells[0].innerHTML) {
            count++;
            
            if(i == rowLength - 1)
            {
            	mergeRows(table_name,field_name,saveIndex, count);
            }
                
        } else {
            mergeRows(table_name,field_name,saveIndex, count);
            
            row = table.rows[i].cells[0].innerHTML;
            saveIndex = i - 1;
            count = 1;
        }
    }
};

function mergeParticipantsTable(){
    mergeTable("table-participants","name")
}
function mergePerformanceParticipantsTable(){
    mergeTable("table-performance-participant","performance_name")
}

$(function () {
    var $result = $('#eventsResult');
    var $table = $('#table-participants');
    var $table = $('#table-performance-participant');
    $('#table-participants').on('post-body.bs.table', function (res) {
      	mergeParticipantsTable();
      })
    $('#table-performance-participant').on('post-body.bs.table', function (res) {
      	mergePerformanceParticipantsTable();
      })         
 })

function addPerformanceDetail(event_id) {
    var performance = document.getElementById("performance");
    var participant = document.getElementById("participant");
     if (performance.selectedIndex == -1){
        flash("Debe seleccionar una interpretación","warning")
        return
    }
    if (participant.selectedIndex == -1){
        flash("Debe seleccionar un participante","warning")
        return
    }
    data = {
        'event_id' : event_id,
        'performance_id' : parseInt(performance.options[performance.selectedIndex].value),
        'participant_id' : parseInt(participant.options[participant.selectedIndex].value)
    }
     
    $.post('/api/performancedetail/add',data ).done( function(msg) { 
            $('#table-performance-participant').bootstrapTable('refresh');
      }).fail( function(xhr, textStatus, errorThrown) {
        flash(xhr.responseText,"error");
    });
};
function deletePerformanceDetailCol(value, row, index){
    return '<i class="glyphicon glyphicon-trash"  onclick="deletePerformanceDetail('+value+')"></i>'       
        
}

function deleteFileCol(value, row, index){
    return '<i class="glyphicon glyphicon-trash"  onclick="deleteFile('+value+')"></i>'               
}

function deletePerformanceDetail(performance_id,participant_id)
{
    $.post('/api/performancedetail/delete', { 'performance_id':performance_id , 'participant_id': participant_id } ).done( function(msg) { 
            $('#table-performance-participant').bootstrapTable('refresh'); 
            $("#participant").val('').trigger('change');
            $("#performance").val('').trigger('change');
            } )
    .fail( function(xhr, textStatus, errorThrown) {
        flash(xhr.responseText,"error");
    });    
}

function deleteFile(medialink_id)
{
    $.post('/api/medialink/delete', { 'medialink_id':medialink_id } ).done( function(msg) { 
            $('#table-medialink').bootstrapTable('refresh'); } )
    .fail( function(xhr, textStatus, errorThrown) {
        flash(xhr.responseText['message'],"error");
    });    
}



function linkCol(value, row, index){
    return '<a class="glyphicon glyphicon-download" href="'+value+'"></a>'            
}

$(function() {
    $('#uploadButton').click(function() {
        event.preventDefault();
        var form_data = new FormData($('#uploadform')[0]);
        form_data.append("description",$('#description')[0].value)

        console.log($('#description'))
        $.ajax({
            type: 'POST',
            url: '/api/uploadajax',
            data: form_data,
            contentType: false,
            processData: false,
            dataType: 'json'
        }).done(function(data, textStatus, jqXHR){

            $('#table-medialink').bootstrapTable('refresh');
            $('#description')[0].value=''

        }).fail(function(xhr, textStatus, errorThrown){
            flash(xhr.responseText,'error');
        });
    });
});