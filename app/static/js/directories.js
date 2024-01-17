/* global bootstrap: false */
var current_directory_id;
var checked_boxes_count = 0

async function postData(url = '', data = {}) {
    const response = await fetch(url, {
        method: 'POST',
        cache: 'no-cache',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    if (response.status == 400) {
        return 'error'
    }
    return response.json()
}

async function uploadPDF() {
    let questionnaire_radio, source;
    const radioButtons = document.querySelectorAll('input[type="radio"]');
    radioButtons.forEach(function (radioButton) {
        if (radioButton.checked) {
            questionnaire_radio = radioButton.id.split('_radio')[0]
            source = radioButton.getAttribute('data-radio-class')
        }
    });
    const jsonObject = { 'parent_id': current_directory_id, 'questionnaire': questionnaire_radio, 'source': source }

    const fileInput = document.getElementById('formFile')
    const file = fileInput.files[0];
    if (!file) {
        alert("Please select a file.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append('json', JSON.stringify(jsonObject))

    const headers = new Headers();
    // Add any custom headers if needed
    // headers.append("Authorization", "Bearer YourToken");

    const requestOptions = {
        method: "POST",
        body: formData
    };

    // Turn spinner on
    document.getElementById('loading-spinner').classList.toggle('hide')
    document.getElementById('upload-form-div').classList.toggle('hide')
    document.getElementById('upload-modal-footer').classList.toggle('hide')

    fetch("/upload_file", requestOptions)
        .then(response => response.json())
        .then((response) => {
            console.log(response)
            if (response['internal_status'] == 1) {
                document.getElementById('loading-spinner').classList.toggle('hide')
                document.getElementById('upload-form-div').classList.toggle('hide')
                document.getElementById('upload-modal-footer').classList.toggle('hide')
                alert(response['message'])
            } else {
                // alert(response['message'])
                location.reload()
            }
        })
}

function row_redirect(row) {
    // Access the row that was clicked
    // // Retrieve the 'data-href' attribute from the row
    const href = '/files/' + row.getAttribute('data-id');
    // // Navigate to the URL specified in 'data-href'
    if (href) {
        window.location.href = href;
    }
}

function add_new_folder() {
    let data = {}
    data['id'] = current_directory_id
    data['name'] = document.getElementById('new_folder_name').value
    if (data['name'] == "") {
        alert("Please name your file")
    } else {
        postData(url = '/create_folder', data = data)
            .then((response) => {
                if (response['internal_status'] == 0) {
                    location.reload()
                } else {
                    $('#new_folder_modal').modal('hide')
                    alert(response['message'])
                    document.getElementById('new_folder_name').value = ''
                }
            })
    }
}

function delete_selected(ids) {
    // // Retrieve the 'data-href' attribute from the row
    postData('/delete_folders', { 'ids': ids })
        .then((response) => {
            if (response['internal_status'] == 0) {
                location.reload()
            } else if (response['internal_status'] == 1) {
                alert(response['message'])
                location.reload()
            } else {
                alert(response['message'])
            }
        })
}


document.addEventListener("DOMContentLoaded", function (event) {
    current_directory_id = window.location.href
    if (current_directory_id.split('/')[current_directory_id.split('/').length - 1] == '') {
        current_directory_id = 'root'
    } else {
        current_directory_id = current_directory_id.split('/')[current_directory_id.split('/').length - 1]
    }

    // Loop through rows
    for (tr of $('tr')) {
        let _id = tr.id
        if (tr.id != '') {
            if (tr.getAttribute('data-file-type') == 'folder') {
                tr.addEventListener('dblclick', () => {
                    const href = '/files/' + _id;
                    window.location.href = href;
                });
            } else {
                tr.addEventListener('dblclick', () => {
                    const href = '/document_chat/' + _id;
                    window.location.href = href;
                });
            }
        }
    }

    $('#save_new_folder').click(add_new_folder)
    $('#upload_file_btn').click(uploadPDF)

    for (box of $('.form-check-input')) {
        box.addEventListener('change', (event) => {
            if (event.currentTarget.checked) {
                checked_boxes_count += 1
            } else {
                checked_boxes_count -= 1
            }
            if (checked_boxes_count == 0) {
                document.getElementById('delete-selected').setAttribute('disabled', 'true')
            } else {
                if (document.getElementById('delete-selected').disabled) {
                    document.getElementById('delete-selected').removeAttribute('disabled')
                }
            }
        })
    }
    document.getElementById('delete-selected').addEventListener('click', () => {
        let ids_to_delete = []
        for (box of $('.form-check-input')) {
            if (box.checked) {
                ids_to_delete.push(box.getAttribute('data-id'))
            }
        }
        delete_selected(ids_to_delete)
    })

    for (star of $('.star-icon')) {
        star.addEventListener('click', (event) => {
            _id = event.currentTarget.getAttribute('data-id')
            postData('/star_file', { 'ids': _id })
                .then((response) => {
                    if (response['internal_status'] == 0) {
                        location.reload()
                    } else if (response['internal_status'] == 1) {
                        alert(response['message'])
                        location.reload()
                    } else {
                        alert(response['message'])
                    }
                })
        })
    }

    document.querySelectorAll('.view_chat_history_reroute_tag').forEach((event) => {
        event.addEventListener('click', function () {
            const redirect_target = event.getAttribute('data-target-url')
            window.location.href = redirect_target;
        })
    })

    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
})