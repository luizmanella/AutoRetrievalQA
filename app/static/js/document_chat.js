var current_document_id;

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

function create_chat_div(text, origin) {
    let newdiv = document.createElement('div')
    newdiv.classList.add('shadow')
    newdiv.classList.add('chat-content')
    newdiv.classList.add('flex-shrink-1')
    if (origin == 'user') {
        newdiv.classList.add('ms-auto')
        newdiv.classList.add('user-question')
    } else {
        newdiv.classList.add('me-auto')
        newdiv.classList.add('llm-response')
    }
    newdiv.appendChild(document.createTextNode(text))
    document.getElementById('chat-space').appendChild(newdiv)
}

function create_thinking_div() {
    let parendiv = document.createElement('div')
    parendiv.classList.add('shadow')
    parendiv.classList.add('chat-content')
    parendiv.classList.add('flex-shrink-1')
    parendiv.classList.add('me-auto')
    parendiv.classList.add('llm-response')
    let spinnerdiv = document.createElement('div')
    spinnerdiv.classList.add('spinner-border')
    spinnerdiv.classList.add('spinner-border-sm')
    spinnerdiv.classList.add('spinner-btn')
    spinnerdiv.innerHTML = '<span class="visually-hidden">Loading...</span>'
    parendiv.appendChild(spinnerdiv)
    return parendiv
}

function send_question() {
    let chat_space = document.getElementById('chat-space')
    question_input_element = document.getElementById('question_input')
    question = question_input_element.value
    if (question != '') {
        // add user question to chat
        create_chat_div(question, 'user')

        // create spinner while backround runs model
        let spinnerdiv = create_thinking_div()
        chat_space.appendChild(spinnerdiv)
        const parent_div = document.getElementById('chat-space')
        const lastElement = parent_div.lastElementChild
        lastElement.scrollIntoView({ 'behavior': 'smooth' })

        // empty input box
        question_input_element.value = ''

        // send question to backend
        postData('/ask_question', { 'question': question, 'document_id': current_document_id })
            .then((response) => {
                // remove spinner
                chat_space.removeChild(chat_space.lastChild)

                // add llm response
                create_chat_div(response, 'llm')
                const parent_div = document.getElementById('chat-space')
                const lastElement = parent_div.lastElementChild
                lastElement.scrollIntoView({ 'behavior': 'smooth' })
            })
    }
}


document.addEventListener("DOMContentLoaded", function (event) {
    current_document_id = window.location.href
    current_document_id = current_document_id.split('/')[current_document_id.split('/').length - 1]

    document.getElementById('question_submit').addEventListener('click', function () {
        send_question()
    })

    document.addEventListener('keypress', function (event) {
        if (event.key == 'Enter') {
            send_question()
        }
    })
})