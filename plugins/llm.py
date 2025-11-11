import os
from core.config import AppConfigManager
from openai import OpenAI
from dictionary.word import PureWord


class LLM():
    def __init__(self, language = 'english'):
        self.language = language

        # this is for gemini.
        google_api_key=os.environ.get("GEMINI_API_KEY")
        if google_api_key != "":
            self.api_key=google_api_key
            self.server_url="https://generativelanguage.googleapis.com/v1beta"
            self.model="gemini-2.5-flash"

        openai_api_key=os.environ.get("OPENAI_API_KEY")
        if openai_api_key != "" and google_api_key == "":
            self.api_key=openai_api_key
            self.server_url="https://api.openai.com/v1"
            self.model="GPT-5"

    def ask(self, message, prompt = "You are a helpful assistant."):

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.server_url
        )

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ]
        )

        # print(response.choices[0].message.content)
        return response.choices[0].message.content

    def openai_dict(self, query_word):
        prompt = """
You are a detailed multilingual dictionary engine.
When the user gives you a word in any language, provide the following details in plain text:

1. Word: the exact word typed
2. Part of Speech: list all applicable
3. Meaning(s): for each meaning, give the following in this exact order and style(could have multiple meaning, label withh 1., 2., 3....):
    Definition:
     - Original: (if original language is Spanish, then we give the definition of it with Spanish and change the label to Spanish)
     - English:
     - Chinese: (traditional)
    Example sentences:(Note. ignore the orignal language traslation. ex. If the original is englsih, then we ignore english traslation.)
     - original-language sentence
       (English translation / Chinese translation)
4. Related phrases: list start with ' - ', include the one-lined meaning with it.
5. Related words: list start with ' - ', include the one-lined meaning with it.
6. Original form and origin: include lemma, verb tense, other forms, and etymology
7. Story / interesting facts: if the word has notable history, anecdotes, or cultural context, include it. If not, skip this section.

Format each meaning separately with its own examples.
Use only spaces for indentation. No bullets, dashes, or special formatting.
Do not use bold or italics. Return plain readable text only.
        """
        message = f"Please provide the dictionary content for the {self.language} word '{query_word}'"

        response = self.ask(message = message, prompt = prompt)

        word_obj = PureWord()
        word_obj.word = query_word

        word_obj.dict_name = "LLM"
        word_obj.meaning = response

        return word_obj
