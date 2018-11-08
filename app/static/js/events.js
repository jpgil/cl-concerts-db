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
            $('#table-performance-participant').bootstrapTable('refresh'); } )
    .fail( function(xhr, textStatus, errorThrown) {
        flash(xhr.responseText,'error');
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
function deleteMusicalEnsembleMember(musical_ensemble_member_id)
{
    $.post('/api/musicalensemblemember/delete', { 'musical_ensemble_member_id': musical_ensemble_member_id } ).done( function(msg) { 
            $('#table-musical-ensemble-members').bootstrapTable('refresh'); } )
           // $('#table-performance-participant').bootstrapTable('refresh'); } )
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
};
function deletePerformanceCol(value, row, index){
    return '<i class="glyphicon glyphicon-trash"  onclick="deletePerformance('+value+')"></i>'           
}
function deletePerformance(performance_id)
{
    $.post('/api/performance/delete', { 'performance_id':performance_id } ).done( function(msg) { 
            $('#table-musical-pieces').bootstrapTable('refresh');
            $('#table-performance-participant').bootstrapTable('refresh');
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
            $('#table-performance-participant').bootstrapTable('refresh'); } )
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
        //event.preventDefault();
        var form_data = new FormData($('#uploadform')[0]);
        form_data.append("description",$('#description')[0].value)
        for (var [key, value] of form_data.entries()) { 
          console.log(key, value);
        }
        console.log($('#description'))
        $.ajax({
            type: 'POST',
            url: '/api/uploadajax',
            data: form_data,
            contentType: false,
            processData: false,
            dataType: 'json'
        }).done(function(data, textStatus, jqXHR){
            console.log(data);
            console.log(textStatus);
            console.log(jqXHR);
            console.log('Success!');
            $('#table-medialink').bootstrapTable('refresh');
            $('#description')[0].value=''
//             $("#resultFilename").text(data['name']);
//            $("#resultFilesize").text(data['size']);
//  here we should update the table
        }).fail(function(xhr, textStatus, errorThrown){
            alert(xhr.responseText);
        });
    });
});
