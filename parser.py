import os
from dotenv import load_dotenv
import openai
from flask import Flask, request, jsonify, send_from_directory, render_template
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

load_dotenv()

from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# data1 = {"recurring_income":1040,"one_time_income":800,"recurring_expenses":1578.1,"one_time_expenses":850.75,"discretionary_expense_percentage":50,"necessary_expense_percentage":50,"savings":1000,"debt_to_income_ratio":0.215,"cash_flow":-538.1,"financial_health_indicators":"Negative cash flow, high recurring expenses, and consistent savings contributions."}
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # This will serve the HTML file



# Function to parse file using Llama Parse
def parse_file(file_path):
    # Assuming llama_parse provides some parse function
    parser = LlamaParse(
        result_type="markdown"  # "markdown" and "text" are available
    )

    file_extractor = {".pdf": parser}
    parsed_data = SimpleDirectoryReader(input_files=[file_path], file_extractor=file_extractor).load_data()
    return parsed_data

# Function to generate graph
# recurring_income: 0, one_time_income: 1, recurring_expenses: 2, one_time_expenses: 3, discretionary_expense_percentage: 4
# necessary_expense_percentage: 5, savings: 6, debt_to_income_ratio: 7, cash_flow: 8, financial_health_indicator: 9
#
def generate_graphs(data, save_dir='/tmp'):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    plt.figure(figsize=(15, 5))

    # Pie chart for discretionary vs. necessary expenses
    plt.subplot(1, 3, 1)
    labels = 'Discretionary', 'Necessary'
    sizes = [data['discretionary_expense_percentage'], data['necessary_expense_percentage']]
    colors = ['gold', 'lightcoral']
    explode = (0.1, 0)  # explode the 1st slice
    plt.pie(sizes, explode=explode, labels=None, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Discretionary vs. Necessary Expenses')
    plt.legend(labels, loc="lower right")
    pie_path = os.path.join(save_dir, 'discretionary_vs_necessary.png')
    plt.savefig(pie_path)

   # Pie chart for debt-to-income ratio with recurring and one-time components
    plt.figure(figsize=(8, 6))

    labels = ['Recurring Income', 'One-Time Income', 'Recurring Expenses', 'One-Time Expenses']
    sizes = [
        data['recurring_income'],
        data['one_time_income'],
        data['recurring_expenses'],
        data['one_time_expenses']
    ]
    colors = ['green', 'lightgreen', 'red', 'pink']
    explode = (0.1, 0.1, 0.1, 0.1)

    plt.pie(sizes, labels=None, colors=colors, explode=explode,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')
    plt.title('Debt-to-Income Ratio (Recurring vs One-Time)')
    plt.legend(labels, loc="lower right")
    ratio_path = os.path.join(save_dir, 'debt_to_income_ratio.png')
    plt.savefig(ratio_path)


    plt.figure(figsize=(15, 5))

    # Savings vs. Cash Flow chart
    plt.subplot(1, 3, 3)
    labels = ['Savings', 'Cash Flow']
    amounts = [data['savings'], data['cash_flow']]
    colors = ['green', 'red']
    bars = plt.bar(labels, amounts, color=colors)
    plt.xlabel('Type')
    plt.ylabel('Amount ($)')
    plt.title('Savings vs. Cash Flow')
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, height / 2, f"${round(height, 2):.2f}", ha='center', va='center', color='white', fontweight='bold')

    flow_path = os.path.join(save_dir, 'savings_vs_cashflow.png')
    plt.savefig(flow_path)

    plt.close('all')

    return {
        'pie_chart': pie_path,
        'debt_to_income_ratio_chart': ratio_path,
        'savings_vs_cashflow_chart': flow_path
    }






@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save file
    file_path = f'/tmp/{file.filename}'
    file.save(file_path)

    # Parse file
    parsed_data = parse_file(file_path)
    
    # Use OpenAI to interpret the parsed data
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "user",
            "content": (
                        f"From the parsed document {parsed_data}, return the following financial information as numbers Show the detailed calculations for each item:"
                        """
                        1. Recurring Income
                        2. One Time Income
                        3. Recurring Expenses
                        4. One Time Expenses
                        5. Percentage of Expenses That Are Discretionary 
                        6. Percentage of Expenses That Are Necessary
                        7. Savings: State the regularity and amount of savings.
                        8. Debt-to-Income Ratio: Calculate the debt-to-income ratio from available data.
                        9. Cash Flow: Calculate the monthly cash flow based on income and expenses.
                        10. Financial Health Indicators: Point out any positive or negative financial habits.

                        Please return the results in a clear and structured format (as numbers) along with the details of your calculations.
                        """
                    ),

            }
        ],
        functions=[
            {
                "name": "return_financial_info",
                "description": "Return financial information in a structured JSON format.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recurring_income": {"type": "number"},
                        "one_time_income": {"type": "number"},
                        "recurring_expenses": {"type": "number"},
                        "one_time_expenses": {"type": "number"},
                        "discretionary_expense_percentage": {"type": "number"},
                        "necessary_expense_percentage": {"type": "number"},
                        "savings": {"type": "number"},
                        "debt_to_income_ratio": {"type": "number"},
                        "cash_flow": {"type": "number"},
                        "financial_health_indicators": {"type": "string"}
                    },
                    "required": [
                        "recurring_income", "one_time_income", "recurring_expenses", 
                        "one_time_expenses", "discretionary_expense_percentage", "necessary_expense_percentage", "savings", 
                        "debt_to_income_ratio", "cash_flow", "financial_health_indicators"
                    ]
                },
            }
        ],
        function_call={
            "name": "return_financial_info"
        }, 
    )



    if response.choices:
        interpretation = response.choices[0].message.content
        # print(interpretation) 
        financial_data = response.choices[0].message.function_call.arguments
        # print(financial_data)
        data = json.loads(financial_data)

        graphs = generate_graphs(data)
        print('HI')

        return jsonify(graphs)
    else:
        return jsonify({'error': 'Failed to interpret document'}), 500
    
    # graphs = generate_graphs(data1)
    # return jsonify(graphs)

@app.route('/tmp/<filename>')
def tmp_file(filename):
    return send_from_directory('/tmp', filename)

if __name__ == '__main__':
    app.run(debug=True)