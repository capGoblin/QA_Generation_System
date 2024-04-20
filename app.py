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

def generate_csv(questions_answers):
    # Define file path for CSV download

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

        # Display extracted text
        st.header("Generating Questions & Answers...")

        with st.status("Generating...", expanded=True) as status:
            st.write("Generating Questions...")
            generated_questions = process_text_and_generate_questions(pdf_text)
            st.write("Generating Answers...")
            generated_questions_answers = generate_ans_for_generated_ques(generated_questions, pdf_text)
            status.update(label="Q & A Generated!", state="complete", expanded=False)    

        # Generate CSV file and allow download
        generate_csv(generated_questions_answers)
            


if __name__ == "__main__":
    main()
