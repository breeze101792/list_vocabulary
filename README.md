# List Vocabulary

## Project Description
`list_vocabulary` is a command-line tool designed to help users manage and learn vocabulary from text files or custom input. It integrates with dictionaries, allows users to track their familiarity with words, and provides an interactive interface for reviewing and memorizing vocabulary. The project aims to make vocabulary acquisition more efficient by providing tools for word extraction, definition lookup, and spaced repetition.

## Features

*   **Word Extraction**: Automatically extracts words from text files, filtering out common words and counting frequencies.
*   **Interactive Dictionary Search**: Look up word definitions from integrated dictionaries (e.g., ECDICT).
*   **Vocabulary Management**: Store and track words in a local SQLite database (`WordBank`), including familiarity levels, times seen, and timestamps.
*   **Memorization Mode**: An interactive mode (`MemorizeListPage`) to review words, mark them as familiar, and progress through different familiarity levels.
*   **Custom Word Lists**: Process words from user-provided text input or SQLite vocabulary builder files (e.g., from Koreader).
*   **Configurable Language Support**: Supports different languages for word filtering.
*   **Debug Mode**: Provides detailed logging for development and troubleshooting.

## Core Concepts

*   **Application Settings**: Manages all the application's settings, file paths, and language preferences, ensuring the tool behaves as you expect.
*   **Text Processor**: This component is responsible for reading your text files, breaking them down into individual words, counting how often each word appears, and filtering out common words you likely already know.
*   **Vocabulary Database**: A local database that stores all your vocabulary words. It keeps track of how familiar you are with each word (on a scale of 0 to 5), how many times you've encountered it, and when you last reviewed it.
    *   **Familiarity Levels**:
        *   `0`: Not relevant or not yet memorized.
        *   `1`: New word; try to remember its meaning. Criteria: Recognize the word when seen (can read it).
        *   `2`: When presented with a Chinese word, you can recall this word. Criteria: Can translate it.
        *   `3`: You can use it in your own sentence.
*   **Dictionary Manager**: Handles connections to various dictionary sources (like ECDICT) to fetch definitions, examples, and suggestions for words.
*   **Interactive Interface**: Provides the foundation for all interactive screens in the application, managing how you navigate, enter commands, and see information.
*   **Dictionary Screen**: An interactive screen dedicated to looking up words, viewing their definitions, and rating your familiarity with them.
*   **Word List Screen**: A screen designed to display and let you navigate through lists of words, such as those extracted from a text file.
*   **Memorization Screen**: An enhanced word list screen specifically for learning. It allows you to hide/show meanings, mark words as familiar, and focus on words you haven't mastered yet for the current day.

## Usage

The main entry point is `pydict.py`.

```bash
./pydict.py --help
```


