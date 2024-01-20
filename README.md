# AutoRetrievalQA - ARQA
![ARQA_logo](https://github.com/luizmanella/AutoRetrievalQA/assets/39210022/3fdd3c5c-c3a7-40b9-9147-938875a55045)

<p>AutoRetrievalQA (ARQA) is an LLM-based application designed to automatically process a document by answering pre-built questionnaires. The project runs as a Flask application deployed through Azure, and is a fully developed web app with authentication handled by Auth0. Users can upload documents and tag them with a specific questionnaire. In the back end, a LLM-based pipeline will process the document and answer the questions of the questionnaire. The app is primed for expansion and improvements. For example, I used cosine similarity to determine the most important parts of the document. The way I break the document to compute the similarity scores is rudimentary and could be improved. Furthermore, if multiple documents are processed with the same questionnaire, business intelligence can be generated from them.</p>

<h2>A Look Under the Hood</h2>
<p>The NLP pipeline is built similarly to a retrival-augmentation-generation (RAG) pipeline, but instead of pulling from multiple documents, it only looks at the document it is trying to extract information from. While building and experimenting with the different LLMs offered by OpenAI, I noticed it was often difficult to prevent the model from <b>NOT</b> bringing outside information when answering questions, but rather <b>ONLY</b> using what it had access to from the document. To do this, I added an additional step to try and prevent this "hallucinatory" step. After an answer has been generated, I feed the parts of the document that was used to obtain the answer and the answer itself into another LLM and ask it to check if the answer could have been obtained from that text. If the answer is "yes", then the response is good to be given back to the user, otherwise, the response was hallucinated and needs to be rejected. I use a predetermined response when that happens.</p> Overall, the process works as follows:
<ol>
    <li>Break the document in batches of nearly equal token count</li>
    <li>Embed each of the batches</li>
    <li>Take a question and embed it as well</li>
    <li>Compute cosine similarity between the question and the batches</li>
    <li>Take the k-most similar batches and use it to answer the question</li>
    <li>Take the answer and the k-most similar batches and run it through the hallucination check</li>
    <li>If hallucinated, then reject, otherwise, accept</li>
</ol>

<h2>Requisite Steps</h2>
<p>In order to start working with the application, you'll need to set up a web application and configure the appropriate resources with Azure. I recommend connecting your GitHub repository to your application so you can use Actions to facilitate creating a CI/CD pipeline. You will also need to create an account and configure resources with Auth0. Lastly, you'll need an account with OpenAI in order to use their pipelines. Once you have configure everything appropriately, you will need the following keys:</p>
<ul>
    <li>AUTH0 CLIENT ID</li>
    <li>AUTH0 CLIENT SECRET</li>
    <li>AUTH0_DOMAIN</li>
    <li>OPEN_AI_KEY</li>
</ul>
<h3>Azure Step - Comment</h3>
<p>Given the way I have step up the project, when you set up the environment in Azure to deploy the web app, you will need to set a <b>Startup Command</b>. Copy and paste the following into the box:</p>
<pre>gunicorn --bind=0.0.0.0 startup:app --timeout 600</pre>

<h3>Additional Steps</h3>
Once you have the prior steps completed, you will want to create an <i>.env</i> file in your project. The environment file will contain environment variables that are used in the app. You may notice the <i>.env</i> file is listed in the <i>.gitignore</i> file. The reason for this is the file is used for local developement, where as you will set the environment variables in Azure with different values. In addition to the keys listed above, you will want to instantiate the following variables:
<ul>
    <li>
        ARQA_PRESETS
        <ul>
            <li>Locally it is the path to the preset questionnaires.</li>
            <li>In deployment, it is the path to a file storage (this can be easily set up with Azure and connected directly to your app)</li>
        </ul>
    </li>
    <li>
        ARQA_USERS
        <ul>
            <li>Locally it is the path to where you will store metadata about a client, such as chat history, document uploads. </li>
            <li>In deployment, it is the path to a file storage as well.
        </ul>
    </li>
    <li>
        APP_SECRET_KEY
        <ul>
            <li>This is a secret variable that you can create but shouldn't share. It's a requisite step in any Flask application. I recommend making a different key for local development and deployment.</li>
        </ul>
    </li>
    <li>
        K_SIMILAR
        <ul>
            <li>This is an integer that represents the number of most similar embedded batches to the user's question which will be used to answer the question. The larger the number, the more information the system can use to answer the question, but the more tokens are required of the LLM.</li>
            <li>The value can be the same locally and globally. It is your choice.</li>
        </ul>
    </li>
    <li>
        MAX_TOKENS
        <ul>
            <li>This value can be the same locally and in deployment. It determines the maximum token variable for the response of the LLM. The value will determine the cost of the responses and the maximum length of the responses.</li>
        </ul>
    </li>
</ul>


<h2>Comments For Developers</h2>
<p>When creating questionnaires, there is a limited number of questions that is not customizable through the website. To change that number, you have to make two small changes. In the "create_questionnaire.js" file, change the variable located at the top, named <i>max_number_of_questions</i>. Next, in the "create_questionnaire.html" file, scro</p>
<p>If your application is specific enough such that many documents are expected to use the same questionnaire, you can create preset questionnaires which would appear at the top of the Questionnaires page, and other appropriate areas. If you have no presets, then nothing will appear. The moment you add one, it will automatically pop-up where intended.</p>
<h3>How to create a preset questionnaire:</h3>
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

<h2>Launching Locally</h2>
<p>Once you have set up Azure and Auth0, and you cloned the repository, recommend setting up a virtual environment and installing the packages in the <i>requirements.txt</i> file. Once you have done this, activate the virtual environment, navigate to the directory containing the <i>startup.py</i> file, and run the following command:</p>
<pre>flask --app app run --debug</pre>
<p>For reference, I like running on debug mode so any changes I make can be seen by simply refreshing the website rather than restarting the app. If you prefer not to, remove the debug tag. Also, if you make any changes to the <i>.env</i> file, you will have to restart the application for the changes to take effect, even if you were on debug mode.</p>

<h2>Future Development</h2>
While I may not develop this application further, I would love to see if it goes anywhere. Reach out with any questions or to let me know how far you've taken it from this point.
