# AutoRetrievalQA
<h1>ARQA</h1>
![Alt Text]([ARQA_logo.jpg](https://github.com/luizmanella/AutoRetrievalQA/blob/main/ARQA_logo.jpeg))
<p>AutoRetrievalQA (ARQA) is an LLM-based application designed to automatically process a document by answering pre-built questionnaires. The project runs as a Flask application, and is a fully developed web app with authentication handled by Auth0. Users can upload documents and tag them with a specific questionnaire. In the back end, a LLM-based pipeline will process the document and answer the questions of the questionnaire. The app is primed for expansion and improvements. For example, we used cosine similarity to determine the most important parts of the document. The way we break the document to compute the similarity scores is rudimentary and could be improved. Furthermore, if multiple documents are processed with the same questionnaire, business intelligence can be generated from them.</p>

<h3>Comments For Developers</h3>
<p>When creating questionnaires, there is a limited number of questions that is not customizable through the website. To change that number, you have to make two small changes. In the "create_questionnaire.js" file, change the variable located at the top, named <i>max_number_of_questions</i>. Next, in the "create_questionnaire.html" file, scro</p>
<p>If your application is specific enough such that many documents are expected to use the same questionnaire, you can create preset questionnaires which would appear at the top of the Questionnaires page, and other appropriate areas. If you have no presets, then nothing will appear. The moment you add one, it will automatically pop-up where intended.</p>
<h5>How to create a preset questionnaire:</h5>
<ol>
    <li>Navigate to the preset_questionnaires directory</li>
    <li>
        In the presets_metadata.json, append a dictionary with the following structure: (For reference tag color is the RGB values)
        {
            "questionnaire_name": "Questionnaire name",
            "tag_color": [
                132, 
                153,
                174
            ],
            "description": "A 20 question questionnaire which covers high level deal/fund structure, investment strategy, and closing mechanics."
        }
    </li>
    <li>
        Now, create a json file with the same name as the "questionnaire_name", with the following structure:
        [
            {
                "#": 0,
                "question": "Question number 1?"
            },
            {
                "#": 1,
                "question": "Question number 2? "
            },
        ]
    </li>
</ol>   
