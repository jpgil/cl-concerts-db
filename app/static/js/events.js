function addParticipant(event_id) {
    var activity = document.getElementById("activity");
    var person = document.getElementById("person");
     if (person.selectedIndex == -1){
        alert("Debe seleccionar una persona")
        return
    }
    if (activity.selectedIndex == -1){
        alert("Debe seleccionar una actividad")
        return
    }
    data = {
        'event_id' : event_id,
        'person_id' : parseInt(person.options[person.selectedIndex].value),
        'activity_id' : parseInt(activity.options[activity.selectedIndex].value)
    }
     
    $.post('/api/participant/add',data ).done( function(msg) { 
            $('#table-participants').bootstrapTable('refresh');
      }).fail( function(xhr, textStatus, errorThrown) {
        alert(xhr.responseText);
    });
};

function deleteParticipantCol(value, row, index){
    return '<i class="glyphicon glyphicon-trash"  onclick="deleteParticipant('+value+')"></i>'           
}
function deleteParticipant(participant_id)
{
    $.post('/api/participant/delete', { 'participant_id':participant_id } ).done( function(msg) { 
            $('#table-participants').bootstrapTable('refresh');} )
    .fail( function(xhr, textStatus, errorThrown) {
        alert(xhr.responseText);
    });    
}


function addPerformance(event_id) {
    var musical_piece = document.getElementById("musical_piece");
    var premiere_type = document.getElementById("premiere_type");
     if (musical_piece.selectedIndex == -1){
        alert("Debe seleccionar una obra")
        return
    }
    if (premiere_type.selectedIndex == -1){
        alert("Debe seleccionar un tipo de estreno")
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
        alert(xhr.responseText);
    });
};
function deletePerformanceCol(value, row, index){
    return '<i class="glyphicon glyphicon-trash"  onclick="deletePerformance('+value+')"></i>'           
}
function deletePerformance(performance_id)
{
    $.post('/api/performance/delete', { 'performance_id':performance_id } ).done( function(msg) { 
            $('#table-musical-pieces').bootstrapTable('refresh'); } )
    .fail( function(xhr, textStatus, errorThrown) {
        alert(xhr.responseText);
    });    
}

function mergeRows(table_name, field_name,index, rowspan) {
    console.log('merging '+field_name, index + ',', rowspan);
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
        alert("Debe seleccionar una interpretación")
        return
    }
    if (participant.selectedIndex == -1){
        alert("Debe seleccionar un participante")
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
        alert(xhr.responseText);
    });
};
function deletePerformanceDetailCol(value, row, index){
    return '<i class="glyphicon glyphicon-trash"  onclick="deletePerformanceDetail('+value+')"></i>'       
        
}

function deletePerformanceDetail(performance_id,participant_id)
{
    $.post('/api/performancedetail/delete', { 'performance_id':performance_id , 'participant_id': participant_id } ).done( function(msg) { 
            $('#table-performance-participant').bootstrapTable('refresh'); } )
    .fail( function(xhr, textStatus, errorThrown) {
        alert(xhr.responseText);
    });    
}