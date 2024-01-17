var selected_color = ['32', '132', '199']
var questions_counter = 1
var checked_boxes_count = 0
var max_number_of_questions = 20


async function getData(url = '', data = {}) {
    let response = await fetch(url);
    if (response.ok) {
        let json = await response.json();
        return json
    } else { alert("HTTP-Error: " + response.status) }
}

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


function create_new_question() {

    if (questions_counter >= max_number_of_questions) {
        alert('You have hit the limit on the number of questions allowed, and therefore cannot add more questions.')
    } else {

        let table = document.getElementById('questionnaire')
        const rowCount = table.rows.length
        let row = table.insertRow(rowCount)
        let cell0 = row.insertCell(0)
        let cell1 = row.insertCell(1)
        let cell2 = row.insertCell(2)
        cell0.innerHTML = `<input class="form-check-input" type="checkbox" value="" data-id="${questions_counter}">`
        cell1.innerHTML = questions_counter + 1
        cell2.innerHTML = `<input name="question" type="text" class="form-control" placeholder="Question" aria-label="question">`
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
        questions_counter = questions_counter + 1
    }
}

function delete_selected(ids) {
    let table = document.getElementById('questionnaire')
    let count_deletions = 0
    for (id of ids) {
        table.deleteRow(id - count_deletions)
        count_deletions += 1
    }
    questions_counter = table.rows.length
    const rows = table.querySelectorAll('tr');

    // Loop through the <tr> elements
    rows.forEach((row, index) => {
        // Access each row
        const cells = row.querySelectorAll('td');
        cells[0].querySelector('input').setAttribute('data-id', index)
        cells[0].querySelector('input').checked = false
        cells[1].innerHTML = index + 1
    });
}


function create_new_questionnaire() {
    let name = document.getElementById('new_questionnaire_name').value
    let tag_color = document.getElementById('tag-color-square').style.color.match(/rgb\((\d+), (\d+), (\d+)\)/)
    tag_color = [tag_color[1], tag_color[2], tag_color[3]]
    let optional_description = document.getElementById('floatingTextarea').value
    if (optional_description == "") {
        optional_description = "-"
    }
    let questions = []
    let table = document.getElementById('questionnaire')
    const rows = table.querySelectorAll('tr');
    rows.forEach((row, index) => {
        // Access each row
        const cells = row.querySelectorAll('td');
        if (cells[2].querySelector('input').value != "") {
            questions.push(cells[2].querySelector('input').value)
        } else {
            console.log('got empty')
        }
    });

    if (questions.length == 0) {
        alert('Must have at least 1 question in order to build the questionnaire.')
        document.getElementById('save-questionnaire').classList.toggle('hide-btn')
        document.getElementById('confirm-save').classList.toggle('hide-btn')
        document.getElementById('cancel-save').classList.toggle('hide-btn')
    } else if (name == "") {
        alert('You must give a name to the questionnaire.')
        document.getElementById('save-questionnaire').classList.toggle('hide-btn')
        document.getElementById('confirm-save').classList.toggle('hide-btn')
        document.getElementById('cancel-save').classList.toggle('hide-btn')
    } else if (questions_counter > 20) {
        alert('You can only have up to 2 questions.')
        document.getElementById('save-questionnaire').classList.toggle('hide-btn')
        document.getElementById('confirm-save').classList.toggle('hide-btn')
        document.getElementById('cancel-save').classList.toggle('hide-btn')
    } else {
        let json_obj = {
            'questionnaire_name': name,
            'tag_color': tag_color,
            'questions': questions,
            'description': optional_description
        }
        postData('/create_questionnaire', json_obj)
            .then((response) => {
                if (response['internal_status'] == 0) {
                    const href = '/questionnaire';
                    // // Navigate to the URL specified in 'data-href'
                    if (href) {
                        window.location.href = href;
                    }
                } else if (response['internal_status'] == 1) {
                    alert(response['message'])
                }
            })
    }
}


function clear_questions_table() {
    const tbody = document.getElementById('questionnaire');
    // Remove all child rows from the tbody
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }
    questions_counter = 0
}

function insert_question(question) {
    let table = document.getElementById('questionnaire')
    const rowCount = table.rows.length
    let row = table.insertRow(rowCount)
    let cell0 = row.insertCell(0)
    let cell1 = row.insertCell(1)
    let cell2 = row.insertCell(2)
    cell0.innerHTML = `<input class="form-check-input" type="checkbox" value="" data-id="${questions_counter}">`
    cell1.innerHTML = questions_counter + 1
    cell2.innerHTML = `<input name="question" type="text" class="form-control" placeholder="Question" aria-label="question">`
    cell2.querySelector('input').value = question
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
    questions_counter = questions_counter + 1
}

function load_preset_into_table(pid) {
    getData(`/load_specific_preset/${pid}`, {})
        .then((response) => {
            console.log(response)
            clear_questions_table()
            for (question of response) {
                console.log(question['question'])
                insert_question(question['question'])
            }
        })
}


document.addEventListener("DOMContentLoaded", function (event) {
    var colorPicker = (function () {
        var config = {
            baseColors: [
                [46, 204, 113],
                [52, 152, 219],
                [155, 89, 182],
                [52, 73, 94],
                [241, 196, 15],
                [230, 126, 34],
                [231, 76, 60]
            ],
            lightModifier: 20,
            darkModifier: 0,
            transitionDuration: 200,
            transitionDelay: 25,
            variationTotal: 10
        };
        var state = {
            activeColor: [0, 0, 0]
        };

        function init() {
            createColorPicker(function () {
                appendBaseColors();
            });

            addEventListeners();

            setFirstColorActive(function () {
                setFirstModifiedColorActive();
            });
        }

        function setActiveBaseColor(el) {
            $('.color.active').removeClass('active');
            el.addClass('active');
        }

        function setActiveColor(el) {
            $('.color-var.active').removeClass('active');
            el.addClass('active');
            state.activeColor = el.data('color').split(',');
            selected_color = el.data('color').split(',')
        }

        function addEventListeners() {
            $('body').on('click', '.color', function () {
                var color = $(this).data('color').split(',');
                setActiveBaseColor($(this));

                hideVariations(function () {
                    createVariations(color, function () {
                        setDelays(function () {
                            showVariations();
                        });
                    });
                });
            });

            $('body').on('click', '.color-var', function () {
                setActiveColor($(this));
            });
        }

        function setFirstColorActive(callback) {
            $('.color').eq(1).trigger('click');
            callback();
        }

        function setFirstModifiedColorActive() {
            setTimeout(function () {
                $('.color-var').eq(7).trigger('click');
            }, 500);
        }

        function createColorPicker(callback) {
            $('.color-picker').append('<div class="base-colors"></div>');
            $('.color-picker').append('<div class="varied-colors"></div>');
            $('.color-picker').append('<div class="active-color"></div>');
            $('.color-picker').append('<div class="color-history"></div>');

            callback();
        }

        function appendBaseColors() {
            for (i = 0; i < config.baseColors.length; i++) {
                $('.base-colors').append('<div class="color" data-color="' + config.baseColors[i].join() + '" style="background-color: rgb(' + config.baseColors[i].join() + ');"></div>');
            }
        };

        function createVariations(color, callback) {
            $('.varied-colors').html('');

            for (var i = 0; i < config.variationTotal; i++) {
                var newColor = [];

                for (var x = 0; x < color.length; x++) {
                    var modifiedColor = (Number(color[x]) - 100) + (config.lightModifier * i);

                    if (modifiedColor <= 0) {
                        modifiedColor = 0;
                    } else if (modifiedColor >= 255) {
                        modifiedColor = 255;
                    }

                    newColor.push(modifiedColor);
                }

                $('.varied-colors').append('<div data-color="' + newColor + '" class="color-var" style="background-color: rgb(' + newColor + ');"></div>');
            }

            callback();
        }

        function setDelays(callback) {
            $('.color-var').each(function (x) {
                $(this).css({
                    'transition': 'transform ' + (config.transitionDuration / 1000) + 's ' + ((config.transitionDelay / 1000) * x) + 's'
                });
            });

            callback();
        }

        function showVariations() {
            setTimeout(function () {
                $('.color-var').addClass('visible');
            }, (config.transitionDelay * config.variationTotal));
        }

        function hideVariations(callback) {
            $('.color-var').removeClass('visible').removeClass('active');

            setTimeout(function () {
                callback();
            }, (config.transitionDelay * config.variationTotal));
        }

        return {
            init: init
        };

    }());
    colorPicker.init();

    document.getElementById('tag-color-square').style.color = `rgb(${selected_color[0]}, ${selected_color[1]}, ${selected_color[2]})`

    document.getElementById('delete-selected').addEventListener('click', () => {
        let ids_to_delete = []
        let skip_first = true
        for (box of $('.form-check-input')) {
            if (skip_first) {
                skip_first = false
            } else {
                if (box.checked) {
                    ids_to_delete.push(box.getAttribute('data-id'))
                }
            }
        }
        document.getElementById('select-all').checked = false
        delete_selected(ids_to_delete)
    })

    document.getElementById('select-color-btn').addEventListener('click', () => {
        document.getElementById('tag-color-square').style.color = `rgb(${selected_color[0]}, ${selected_color[1]}, ${selected_color[2]})`
        $(document.getElementById('color_picker')).modal('hide')
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
        let table = document.getElementById('questionnaire')
        if (event.currentTarget.checked) {
            const rows = table.querySelectorAll('tr');
            rows.forEach((row, index) => {
                // Access each row
                const cells = row.querySelectorAll('td');
                cells[0].querySelector('input').setAttribute('data-id', index)
                cells[0].querySelector('input').checked = true
            });
            document.getElementById('delete-selected').removeAttribute('disabled')
        } else {
            const rows = table.querySelectorAll('tr');
            rows.forEach((row, index) => {
                // Access each row
                const cells = row.querySelectorAll('td');
                cells[0].querySelector('input').setAttribute('data-id', index)
                cells[0].querySelector('input').checked = false
            });
            document.getElementById('delete-selected').setAttribute('disabled', 'true')
        }
    })

    document.getElementById('save-questionnaire').addEventListener('click', function () {
        console.log('clicked save')
        document.getElementById('save-questionnaire').classList.toggle('hide-btn')
        document.getElementById('confirm-save').classList.toggle('hide-btn')
        document.getElementById('cancel-save').classList.toggle('hide-btn')
    })
    document.getElementById('cancel-save').addEventListener('click', function () {
        document.getElementById('save-questionnaire').classList.toggle('hide-btn')
        document.getElementById('confirm-save').classList.toggle('hide-btn')
        document.getElementById('cancel-save').classList.toggle('hide-btn')
    })

    for (preset_btn of document.querySelectorAll('.preset-questionnaire-pull-btns')) {
        console.log(preset_btn)
        preset_btn.addEventListener('click', function (event) {
            load_preset_into_table(this.id)

        })
    }
})