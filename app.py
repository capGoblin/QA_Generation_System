import streamlit as st
from PyPDF2 import PdfReader
import csv
from qa_generation_system import process_text_and_generate_questions, generate_ans_for_generated_ques

# Function to extract text from PDF file
def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def generate_csv():
    # Define file path for CSV download
    questions_answers = {'=== TRUE/FALSE QUESTIONS ===': '=== ANSWERS BELOW ===', '1. The Big Mac Index was introduced by The Economist in 1986 as a serious tool for evaluating exchange rates. (True/False)': 'false', '2. The Big Mac Index compares the relative price of purchasing a Big Mac worldwide. (True/False)': 'true', '3. The Big Mac Index is used to calculate the implied exchange rate between two currencies. (True/False)': 'true', "4. The Big Mac Index methodology is limited by geographical coverage due to the presence of the McDonald's franchise. (True/False)": 'true', "5. The Big Mac Index is a perfect representation of a country's economy as a whole. (True/False)": 'false', '=== MULTIPLE CHOICE QUESTIONS ===': '=== ANSWERS BELOW ===', "1. What is the purpose of The Economist's Big Mac Index? A. To measure the popularity of fast food chains worldwide B. To compare the prices of Big Macs in different countries C. To evaluate the nutritional value of Big Macs D. To determine the best marketing strategies for McDonald's": 'B. TO COMPARE THE PRICES OF BIG MACS IN DIFFERENT COUNTRIES', '2. How is the implied exchange rate calculated in the Big Mac Index? A. By dividing the price of a Big Mac in a foreign country by the price in the base country B. By comparing the prices of various fast food items globally C. By analyzing the GDP of different countries D. By converting the prices of Big Macs into gold prices': 'A. BY DIVIDING THE PRICE OF A BIG MAC IN A FOREIGN COUNTRY BY THE PRICE IN THE BASE COUNTRY', "3. What is a limitation of the Big Mac Index based on the text? A. It does not take into account the social status of eating at fast food restaurants B. It only focuses on the prices of Big Macs in developed countries C. It relies on the availability of McDonald's restaurants in each country D. It does not consider the nutritional value of the Big Mac": "C. IT RELIES ON THE AVAILABILITY OF MCDONALD'S RESTAURANTS IN EACH COUNTRY", "4. How did the Argentine government manipulate the Big Mac Index according to the text? A. By artificially inflating the prices of Big Macs B. By forcing McDonald's to sell Big Macs at lower prices C. By closing down McDonald's restaurants in the country D. By introducing a new variation of the Big Mac Index": "B. BY FORCING MCDONALD'S TO SELL BIG MACS AT LOWER PRICES", "5. What is a criticism of using the Big Mac Index for evaluating purchasing power parity? A. It does not account for the cost of shipping products B. It only focuses on the prices of fast food items C. It relies on the availability of McDonald's restaurants D. It does not consider the social status of eating at fast food chains": "C. IT RELIES ON THE AVAILABILITY OF MCDONALD'S RESTAURANTS", '=== ONE-WORD ANSWER QUESTIONS ===': '=== ANSWERS BELOW ===', '1. Purpose?': 'comparison', '2. Year introduced?': '1986', '3. Calculation method?': 'implied', '4. Limitations?': 'geographical', '5. Variants?': 'no', '6. Manipulation example?': 'argentina'}

    csv_file_path = "generated_questions_answers.csv"

    # Write questions and answers to CSV file
    with open(csv_file_path, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # Write headers
        csv_writer.writerow(["Question", "Answer"])

        # Write each question and answer pair
        for question, answer in questions_answers.items():
            csv_writer.writerow([question, answer])

    with open(csv_file_path, 'r') as file:
                csv_data = file.read()
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="generated_questions_answers.csv",
                    mime="text/csv"
                )
    return csv_file_path


# Streamlit app
def main():
    st.title("PDF to Questions and Answers")

    # File upload
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf", accept_multiple_files=False)

    if uploaded_file is not None:
        # Display uploaded file
        st.write("Uploaded PDF file:", uploaded_file.name)

        # Extract text from PDF
        pdf_text = extract_text_from_pdf(uploaded_file)

        # Generate CSV file and allow download
        generate_csv()
            
        # Display extracted text
        st.header("Generating Questions & Answers...")


        # with st.status("Generating...", expanded=True) as status:
        #     st.write("Generating Questions...")
        #     generated_questions = process_text_and_generate_questions(pdf_text)
        #     st.write("Generating Answers...")
        #     generated_questions_answers = generate_ans_for_generated_ques(generated_questions, pdf_text)
        #     status.update(label="Q & A Generated!", state="complete", expanded=False)
    


if __name__ == "__main__":
    main()
