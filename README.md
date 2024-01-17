# AutoRetrievalQA
If your application is specific towards some specific set of documents, you can create preset questionnaires which would appear at the top of the Questionnaires page.
If you have no presets, then nothing will appear. The moment you add one, it will automatically pop-up where intended.
You accomplish this by doing the following:
- Navigate to the preset_questionnaires
- in the presets_metadata.json, append a dictionary with the following structure: (For reference tag color is the RGB values)
    {
        "questionnaire_name": "Questionnaire name",
        "tag_color": [
            132, 
            153,
            174
        ],
        "description": "A 20 question questionnaire which covers high level deal/fund structure, investment strategy, and closing mechanics."
    }
- Now, create a json file with the same name as the "questionnaire_name". The following is a sample idea:
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


The questionnaire has a limited number of questions allowed. If you want to increase the number you must change the variable "max_number_of_questions" in the "create_questionnaire.js" file.