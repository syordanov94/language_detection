from tkinter import filedialog
import string

CNST_TEXT_LINE_NAME = "Text"
CNST_TEST_LANGDETECT_LANG_LINE_NAME= "Langdetect predicted language"
CNST_TEST_LANGDETECT_PROB_LINE_NAME = "Langdetect probability"
CNST_TEST_LANGID_LANG_LINE_NAME= "Langid predicted language"
CNST_TEST_LANGID_PROB_LINE_NAME = "Langid probability"

CNST_LANG_DETECTION_RESULTS_FILE_NAME = "lang_detection_results.csv"
CNST_LANG_DETECTION_DIFFERENCES_FILE_NAME = "lang_detection_differences.csv"

def detect_language_with_langdetect(line): 
    from langdetect import detect_langs 
    lang = ""
    prob = {}
    try: 
        langs = detect_langs(line) 
        for item in langs: 
            if item.lang == "en": 
                return item.lang, item.prob 
            else: 
                lang = item.lang 
                prob = item.prob 
            return lang, prob 
    except: return "err", 0.0 
    
def detect_language_with_langid(line): 
    from py3langid.langid import LanguageIdentifier, MODEL_FILE 
    identifier = LanguageIdentifier.from_pickled_model(MODEL_FILE, norm_probs=True) 
    lang, prob = identifier.classify(line) 
    if lang == "en": 
        return lang, prob
    return lang, prob

def write_data_to_csv(lines, langdetect_lang_results, langdetect_prob_results, langid_lang_results, langid_prob_results): 
    import pandas as pd 
    data = { CNST_TEXT_LINE_NAME: lines, 
            CNST_TEST_LANGDETECT_LANG_LINE_NAME: langdetect_lang_results, 
            CNST_TEST_LANGDETECT_PROB_LINE_NAME: langdetect_prob_results, 
            CNST_TEST_LANGID_LANG_LINE_NAME: langid_lang_results, 
            CNST_TEST_LANGID_PROB_LINE_NAME: langid_prob_results, } 
    df = pd.DataFrame(data) 
    df.to_csv(CNST_LANG_DETECTION_RESULTS_FILE_NAME, sep="|")


def extract_differences(file_name):
    import pandas as pd
    df = pd.read_csv(file_name, sep="|")
    
    langdetect_predicted_lang = {}
    langid_predicted_lang = {}

    # --- (1) ----
    # Recover all the rows there the algorythms predicted a different value
    for _, row in df.iterrows():
        #This is done assuming that both algortithms use the same ISO-2 lang code
        if row[CNST_TEST_LANGDETECT_LANG_LINE_NAME] != row[CNST_TEST_LANGID_LANG_LINE_NAME]:
            if row[CNST_TEXT_LINE_NAME] not in langdetect_predicted_lang:
                langdetect_predicted_lang[row[CNST_TEXT_LINE_NAME]] = row[CNST_TEST_LANGDETECT_LANG_LINE_NAME]
            if row[CNST_TEXT_LINE_NAME] not in langid_predicted_lang:
                langid_predicted_lang[row[CNST_TEXT_LINE_NAME]]= row[CNST_TEST_LANGID_LANG_LINE_NAME]

    # --- (2) ----
    # Store these values in a new csv file
    data = { CNST_TEXT_LINE_NAME: langdetect_predicted_lang.keys(), 
            CNST_TEST_LANGDETECT_LANG_LINE_NAME: langdetect_predicted_lang.values(),
            CNST_TEST_LANGID_LANG_LINE_NAME: langid_predicted_lang.values(),} 
    df = pd.DataFrame(data)
    df.to_csv(CNST_LANG_DETECTION_DIFFERENCES_FILE_NAME, sep="|")


def show_lang_algorithm_detection_chart(axes, df, predicted_lang_csv_line, img_positions):
    import pandas as pd

    lang_data = {}
    for _, row in df.iterrows():
        if row[predicted_lang_csv_line] in lang_data:
            lang_data[row[predicted_lang_csv_line]] += 1
        else:
            lang_data[row[predicted_lang_csv_line]] = 1

    data = {'numberoflines': lang_data.values()}
    df_lang_id = pd.DataFrame(data, index=lang_data.keys())
    explode = []
    num_keys = len(lang_data.keys())
    for i in range(num_keys):
        explode.append(0.05)

    df_lang_id.plot.pie(y='numberoflines', figsize=(20, 10), autopct='%1.1f%%', startangle=90, legend=False, title=predicted_lang_csv_line + " values",explode=explode,ax=axes[img_positions[0]][img_positions[1]])


def show_lang_agorithm_mean_probability_chart(axes, df, positions, predicted_lang_csv_line, predicted_lang_prob_csv_line):
    from statistics import mean
    import pandas as pd

    prob_data = {}
    for index, row in df.iterrows(): 
        if row[predicted_lang_csv_line] not in prob_data:
            prob_data[row[predicted_lang_csv_line]] = []
        prob_data[row[predicted_lang_csv_line]].append(row[predicted_lang_prob_csv_line])
 
    mean_data = {}
    for key, value in prob_data.items():
        mean_data[key] = mean(value)
    
    sortedDict = dict(sorted(mean_data.items(), key=lambda x: x[0].lower()))

    df_lang_detect_meam = pd.DataFrame({'prob': sortedDict.values()}, index=sortedDict.keys())
    ax = df_lang_detect_meam.plot.barh(y='prob',ax=axes[positions[0]][positions[1]],legend=False)
    ax.bar_label(ax.containers[0])
    return ax

def show_results(file_name):
    import pandas as pd
    import matplotlib.pyplot as plt
    df = pd.read_csv(file_name, sep="|")
    fig, axes = plt.subplots(2,2)
    pd.set_option("display.max_rows", None)

    # --- (1) ----
    # Plot the langid results
    show_lang_algorithm_detection_chart(axes, df, CNST_TEST_LANGID_LANG_LINE_NAME, [0,0])

    # --- (2) ----
    # Plot the langid results
    show_lang_algorithm_detection_chart(axes, df, CNST_TEST_LANGDETECT_LANG_LINE_NAME, [0,1])

    # --- (3) ----
    # Plot the mean probability for each language and each case
    show_lang_agorithm_mean_probability_chart(axes, df, [1,0], CNST_TEST_LANGID_LANG_LINE_NAME, CNST_TEST_LANGID_PROB_LINE_NAME)
    show_lang_agorithm_mean_probability_chart(axes, df, [1,1], CNST_TEST_LANGDETECT_LANG_LINE_NAME, CNST_TEST_LANGDETECT_PROB_LINE_NAME)

    plt.show()


# --- (1) -----
# Open File abd recover all the lines
file_path = filedialog.askopenfilename()
with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

langdetect_lang_results = []
langdetect_prob_results = []
langid_lang_results = []
langid_prob_results = []
raw_text = []

for i in range(1, len(lines)):
    
    lines[i] = lines[i].translate(str.maketrans('', '', string.punctuation)).rstrip()
    
    raw_text.append(lines[i])

    # --- (2) -----
    # Run langdetect algorythm and get the most "relevant" language and it's threshold
    langdetect_lang, langdetect_prob = detect_language_with_langdetect(lines[i])
    langdetect_lang_results.append(langdetect_lang)
    langdetect_prob_results.append(langdetect_prob)

    # --- (3) ----- 
    # Run the langid translate algorythm and get the most "relevant" language 
    langid_lang, langid_prob = detect_language_with_langid(lines[i]) 
    langid_lang_results.append(langid_lang) 
    langid_prob_results.append(langid_prob)

# --- (6) ----
# Proces data and add it to excel
write_data_to_csv(raw_text, langdetect_lang_results, langdetect_prob_results ,langid_lang_results, langid_prob_results)
# --- (7) ----
# Extract a subset of the PDF where the predicted languages of each algorithm differ
extract_differences(CNST_LANG_DETECTION_RESULTS_FILE_NAME)
# --- (8) ----
# Plot results
show_results(CNST_LANG_DETECTION_RESULTS_FILE_NAME)