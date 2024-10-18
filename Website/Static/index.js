function deleteNote(noteId){
    fetch('/delete-note',{
        method: 'POST',
        body: JSON.stringify({ noteId: noteId}),
    }).then((_res) => {
        window.location.href = '/';
    });
}
function refresh_notice(){
    fetch('/refresh_notice',{
        method: 'POST',
        body: JSON.stringify(),
    }).then((_res) => {
        window.location.href = '/';
    });
}

function deleteFile(fId){
    fetch('/delete-file/' + fId,{
        method: 'DELETE',
        body: JSON.stringify({ fId: fId}),
    }).then((_res) => {
        
        window.location.href = '/';
    });
}



