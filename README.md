# BankLoan

**BankLoan** is a tool that processes bank statements and assists in determining whether a loan should be granted. By parsing PDF documents of bank statements and utilizing AI-powered analysis, the program automates the decision-making process and provides users with clear, visual insights into financial data.

## Features

- **PDF Parsing:** Uses [LlamaParse](https://github.com/run-llama/llama_parse) to parse bank statement PDFs and extract relevant data.
- **Data Analysis:** Leverages OpenAI's API to analyze the extracted data and generate insights.
- **Visual Insights:** Displays key information and analysis results in easily understandable graphs.
- **Loan Decision Assistance:** Provides the user with the visual data needed to make an informed decision about whether to grant a loan.
- **Efficiency:** Saves time by automating the process of parsing and analyzing bank statements.

## How It Works

1. **Parsing Bank Statements:** The program begins by parsing PDF bank statements using LlamaParse. This step extracts financial data such as income, expenses, and balance.
2. **AI-Powered Analysis:** The extracted data is then passed to the OpenAI API, which generates insightful information and values based on the bank statement content.
3. **Visual Representation:** The returned values are visualized using graphs, giving the user a clear, high-level overview of the financial data.
4. **Loan Evaluation:** Based on the visualizations, the user can easily decide whether to approve or reject the loan application.

## Benefits

- **Faster Decision Making:** Quickly analyze multiple bank statements and generate visuals to support faster loan decisions.
- **Automated Processing:** No need for manual parsing of bank statement PDFs – the tool does it automatically.
- **Clear Insights:** Visual graphs make it easy for users to understand financial data and make informed loan decisions.
- **Time-Saving:** Significantly reduces the time spent reviewing documents manually, improving overall efficiency.

## Installation

To install and run the program locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/PDC8/BankLoan.git
   ```
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the program:
    ```bash
    python parser.py
    ```

## Technologies Used
- **LlamaParse**
- **OpenAI API** 
- **Matplotlib** 
- **Flask** 

