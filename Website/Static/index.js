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

//POPUP when adding new service
document.getElementById('addServiceBtn').addEventListener('click', function() {
    document.getElementById('overlay').style.display = 'block';
    document.getElementById('popup').style.display = 'block';
});

document.getElementById('closeBtn').addEventListener('click', function() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('popup').style.display = 'none';
});

// Close the popup when clicking outside of it
document.getElementById('overlay').addEventListener('click', function() {
    this.style.display = 'none';
    document.getElementById('popup').style.display = 'none';
});
