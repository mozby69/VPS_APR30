
// auto generated emb code
$('#addEmployeeModal').on('shown.bs.modal', function (e) {
    // Make an AJAX request to get the next available code
    fetch('/get_next_code/')
       .then(response => response.json())
       .then(data => {
          // Update the code input with the next available code
          document.getElementById('code').value = data.code;
       })
       .catch(error => console.error('Error:', error));
 });





 



