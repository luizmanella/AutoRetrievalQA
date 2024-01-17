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


function delete_selected(qids) {
    // // Retrieve the 'data-href' attribute from the row
    postData('/delete_questionnaire', { 'qids': qids })
        .then((response) => {
            if (response['internal_status'] == 0) {
                location.reload()
            } else {
                alert(response['message'])
            }
        })
}



document.addEventListener("DOMContentLoaded", function (event) {

    document.getElementById('delete-selected').addEventListener('click', () => {
        let qids_to_delete = []
        let skip_first = true
        for (box of $('.form-check-input')) {
            if (skip_first) {
                skip_first = false
            } else {
                if (box.checked) {
                    qids_to_delete.push(box.getAttribute('data-id'))
                }
            }
        }
        delete_selected(qids_to_delete)
    })

    let skip_first = true
    for (box of $('.form-check-input')) {
        if (skip_first) {
            skip_first = false
        } else {
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
    }
    document.getElementById('select-all').addEventListener('change', (event) => {
        let table = document.getElementById('questionnaire-list')
        if (event.currentTarget.checked) {
            const rows = table.querySelectorAll('tr');
            rows.forEach((row, index) => {
                // Access each row
                const cells = row.querySelectorAll('td');
                cells[0].querySelector('input').checked = true
            });
            document.getElementById('delete-selected').removeAttribute('disabled')
        } else {
            const rows = table.querySelectorAll('tr');
            rows.forEach((row, index) => {
                // Access each row
                const cells = row.querySelectorAll('td');
                cells[0].querySelector('input').checked = false
            });
            document.getElementById('delete-selected').setAttribute('disabled', 'true')
        }
    })

    // Loop through rows
    for (tr of $('tr')) {
        let _id = tr.id
        if (tr.id != '') {
            tr.addEventListener('dblclick', () => {
                const href = '/view_questionnaire/' + _id;
                window.location.href = href;
            });
        }
    }
})