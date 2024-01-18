# AutoRetrievalQA - ARQA
![image](https://github.com/luizmanella/AutoRetrievalQA/assets/39210022/1e012340-bd33-4871-8b79-f67e1788a094)

<p>AutoRetrievalQA (ARQA) is an LLM-based application designed to automatically process a document by answering pre-built questionnaires. The project runs as a Flask application deployed through Azure, and is a fully developed web app with authentication handled by Auth0. Users can upload documents and tag them with a specific questionnaire. In the back end, a LLM-based pipeline will process the document and answer the questions of the questionnaire. The app is primed for expansion and improvements. For example, we used cosine similarity to determine the most important parts of the document. The way we break the document to compute the similarity scores is rudimentary and could be improved. Furthermore, if multiple documents are processed with the same questionnaire, business intelligence can be generated from them.</p>

<h3>Requisite Steps</h3>
<p>In order to start working with the application, you'll need to set up a web application and configure the appropriate resources with Azure. I recommend connecting your GitHub repository to your application so you can use Actions to facilitate creating a CI/CD pipeline. You will also need to create an account and configure resources with Auth0. Lastly, you'll need an account with OpenAI in order to use their pipelines. Once you have configure everything appropriately, you will need the following keys:</p>
<ul>
    <li>AUTH0 CLIENT ID</li>
    <li>AUTH0 CLIENT SECRET</li>
    <li>AUTH0_DOMAIN</li>
    <li>OPEN_AI_KEY</li>
</ul>
<h5>Additional Steps</h5>
Once you have the prior steps completed, you will want to create an <i>.env</i> file in your project. The environment file will contain environment variables that are used in the app. You may notice the <i>.env</i> file is listed in the <i>.gitignore</i> file. The reason for this is the local file is used for local developement, where as you will set the environment variables in Azure with different values. In addition to the keys listed above, you will want to instantiate the following variables:
<ul>
    <li>
        ARQA_PRESETS
        <ul>
            <li>Locally it is the path to the preset questionnaires (i.e. app/preset_questionnaires)</li>
            <li>Globally, it is the path to a file storage (this can be easily set up with Azure and connected directly to your app)</li>
        </ul>
    </li>
    <li>
        ARQA_USERS
        <ul>
            <li>Locally it is the path to where you will store metadata about a client (i.e. app/arqa_users). It is not sensitive information. </li>
        </ul>
    </li>
</ul>

<h3>Comments For Developers</h3>
<p>When creating questionnaires, there is a limited number of questions that is not customizable through the website. To change that number, you have to make two small changes. In the "create_questionnaire.js" file, change the variable located at the top, named <i>max_number_of_questions</i>. Next, in the "create_questionnaire.html" file, scro</p>
<p>If your application is specific enough such that many documents are expected to use the same questionnaire, you can create preset questionnaires which would appear at the top of the Questionnaires page, and other appropriate areas. If you have no presets, then nothing will appear. The moment you add one, it will automatically pop-up where intended.</p>
<h5>How to create a preset questionnaire:</h5>
<ol>
    <li>Navigate to the preset_questionnaires directory</li>
    <li>
        In the presets_metadata.json, append a dictionary with the following structure: (For reference, the <i>tag_color</i> contain the RGB values)
        <pre>
        {
            "questionnaire_name": "Questionnaire name",
            "tag_color": [132, 153, 174],
            "description": "A 20 question questionnaire which covers high level deal/fund structure, investment strategy, and closing mechanics."
        }
        </pre>
    </li>
    <li>
        Now, create a json file with the same name as the "questionnaire_name", with the following structure:
        <pre>
        [
            {"#": 0, "question": "Question number 1?"},
            {"#": 1, "question": "Question number 2?"}, 
            ...
        ]
        </pre>
    </li>
</ol>   
